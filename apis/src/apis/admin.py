from collections import Counter
from datetime import datetime
from io import BytesIO
from http import HTTPStatus
from zipfile import ZipFile
from typing import Annotated


from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, delete, distinct, func, update, text
from sqlalchemy import orm
from sqlalchemy.exc import DBAPIError

from apis.shared.fftt_api import get_player_fftt
from apis.shared.db import (
    CategoryInDB,
    PlayerInDB,
    EntryInDB,
    is_before_cutoff,
)
import apis.shared.api_errors as ae
from apis.shared.custom_decorators import after_cutoff
from apis.shared.models import (
    Player,
    AliasedBase,
    EntryWithPlayer,
    ContactInfo,
)
from apis.shared.dependencies import get_rw_session, get_ro_session, Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EntryInfo(AliasedBase):
    category_id: str
    marked_as_present: bool | None
    marked_as_paid: bool


@app.post("/entries/<licence_no>")
def api_admin_register_entries(
    licence_no: str,
    entries: list[EntryInfo],
    total_actual_paid: int,
    session: Annotated[orm.Session, Depends(get_rw_session)],
):
    """
    expects a json payload of the form: {"totalActualPaid": XX, "entries": [{...}, ...]}
    with entries of the form:
    {"categoryId": "X", "markedAsPresent": true/false/null, "markedAsPaid": true/false}

    The endpoint considers the payload to represent all the entries for the player
    after the request. In particular, it deletes all entries for the player that are not
    in the payload, and updates the other entries with the information in the payload.
    The endpoint also updates the totalActualPaid field of the player with the value
    in the payload.
    The endpoint preserves the registration_time of the entries that are not deleted.

    Note that the endpoint consciously does not enforce the following constraints,
    allowing the admin to override them if need be:
    - the player must not register to more than MAX_ENTRIES_PER_DAY categories per day
    - if female, the player must register to the women_only category of the day if she
        registers to any category of the day

    Enforced format/logic constraints:
    - totalActualPaid field must be present and not null
    - the licence_no must correspond to an existing player in the database
    - the entries must be correctly formatted
    - the category_ids must correspond to existing categories in the database
    - the player must be able to register to all categories indicated w.r.t
        gender/points constraints
    - the request must not try to register to more than one category of the same color
    - the request must not try to mark entries as present before cutoff
    - the request must not try to mark entries as present for categories that have
        already max_players present players
    - the totalActualPaid field must not be higher than the total fees for all entries
    """
    origin = api_admin_register_entries.__name__

    player = session.get(PlayerInDB, licence_no)
    # checks that the player exists in the database (not just in FFTT)
    if player is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    new_entry_category_ids = {entry.category_id for entry in entries}
    old_entries = list(player.entries)
    old_entry_category_ids = {entry.category_id for entry in old_entries}

    # checks that all category ids are valid
    nonexisting_category_ids = new_entry_category_ids.difference(
        session.scalars(select(CategoryInDB.category_id)),
    )
    if nonexisting_category_ids:
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
            payload={
                "categoryIds": sorted(nonexisting_category_ids),
            },
        )

    # We use list comprehension here instead of session.scalars(
    # select(Category).where(Category.category_id.in_(new_entry_category_ids))
    # ).all() to preserve the order.
    potential_categories = [
        session.get(CategoryInDB, entry.category_id) for entry in entries
    ]
    # checks that the player can register to all categories indicated
    # w.r.t gender/points constraints
    gender_points_violations = [
        category.category_id
        for category in potential_categories
        if not player.respects_gender_points_constraints(category)
    ]
    if gender_points_violations:
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.GENDER_POINTS_VIOLATION_MESSAGE,
            payload={
                "categoryIds": sorted(gender_points_violations),
            },
        )

    # checks that the player does not try to register to
    # more than one category of the same color
    max_entries_per_color = max(
        Counter(
            category.color
            for category in potential_categories
            if category.color is not None
        ).values()
        or [0],
    )
    if max_entries_per_color > 1:
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.COLOR_VIOLATION_MESSAGE,
        )

    # checks that the request does not try to mark entries as present
    # before the registration period has ended (marking as absent is possible)
    if is_before_cutoff():
        present_category_ids = [
            entry.category_id for entry in entries if entry.marked_as_present is True
        ]
        if present_category_ids:
            raise ae.RegistrationCutoffError(
                origin=origin,
                error_message=ae.RegistrationMessages.NOT_ENDED_MARK_PRESENT_MAKE_PAYMENT,
                payload={
                    "categoryIdsPresent": present_category_ids,
                },
            )

    # checks that the request does not try to mark entries as present
    # for categories that have already max_players present players
    # (and that were not previously marked as present).
    # Note that here new entries are not yet associated with the session,
    # which implies that the session.get(Entry, ...) call only returns old entries.
    # However, this also means that we have to use session.get(Category, ...)
    # instead of simply entry.category.
    category_ids_with_too_many_present = [
        entry.category_id
        for entry in entries
        if (
            entry.marked_as_present is True
            and (
                entry.category_id not in old_entry_category_ids
                or session.get(
                    EntryInDB,
                    (entry.category_id, licence_no),
                ).marked_as_present
                is not True
            )
            and len(session.get(CategoryInDB, entry.category_id).present_entries())
            >= session.get(CategoryInDB, entry.category_id).max_players
        )
    ]
    if category_ids_with_too_many_present:
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.CATEGORY_FULL_PRESENT_MESSAGE,
            payload={
                "categoryIds": sorted(category_ids_with_too_many_present),
            },
        )

    # we need to update the session objects here to be able to compute the
    # fees_total_present for the last constraint check.
    # we actually need to use the relationship syntax instead of the
    # session.add/delete syntax because the latter does not update the
    # relationships before committing, and we need updated relationships
    # for the computation of fees_total_present
    for i, entry in list(enumerate(old_entries))[::-1]:
        if entry.category_id not in new_entry_category_ids:
            del player.entries[i]

    for entry, category in zip(entries, potential_categories):
        entry.licence_no = licence_no
        if entry.category_id not in old_entry_category_ids:
            entry.registration_time = datetime.now()
            player.entries.append(entry)
            category.entries.append(entry)
        else:
            session.merge(entry)

    player.total_actual_paid = total_actual_paid

    try:
        session.commit()
    except DBAPIError as e:
        session.rollback()
        raise ae.UnexpectedDBError(
            origin=origin,
            exception=e,
        )

    return player


@app.delete("/players/<licence_no>")
def api_admin_delete_player(
    licence_no: str,
    session: Annotated[orm.Session, Depends(get_rw_session)],
):
    origin = api_admin_delete_player.__name__
    player_in_db = session.get(PlayerInDB, licence_no)
    if player_in_db is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    try:
        session.delete(player_in_db)
        session.commit()
        return Response(status_code=HTTPStatus.NO_CONTENT)
    except DBAPIError as e:
        session.rollback()
        raise ae.UnexpectedDBError(
            origin=origin,
            exception=e,
        )


class BibNumber(AliasedBase):
    licence_no: str
    bib_no: int


@app.post("/bibs")
@after_cutoff
def api_admin_assign_all_bibs(session: Annotated[orm.Session, Depends(get_rw_session)]):
    origin = api_admin_assign_all_bibs.__name__
    players_with_bibs = session.scalars(
        select(PlayerInDB.licence_no).where(PlayerInDB.bib_no.isnot(None)),
    ).all()
    if players_with_bibs:
        raise ae.BibConflictError(
            origin=origin,
            error_message=ae.SOME_BIBS_ALREADY_ASSIGNED_MESSAGE,
            payload={"licenceNos": sorted(players_with_bibs)},
        )

    licence_nos = session.scalars(
        select(PlayerInDB.licence_no)
        .join_from(PlayerInDB, EntryInDB)
        .join(CategoryInDB)
        .group_by(PlayerInDB.licence_no)
        .order_by(func.min(CategoryInDB.start_time), PlayerInDB.licence_no),
    )
    assigned_bib_nos = [
        BibNumber(licence_no=licence_no, bib_no=(i + 1))
        for i, licence_no in enumerate(licence_nos)
    ]
    try:
        session.execute(update(PlayerInDB), [x.model_dump() for x in assigned_bib_nos])
        session.commit()
    except DBAPIError as e:
        session.rollback()
        raise ae.UnexpectedDBError(
            origin=origin,
            exception=e,
        )
    return assigned_bib_nos


@app.put("/bibs/<licence_no>")
@after_cutoff
def api_admin_assign_one_bib(
    licence_no: str,
    session: Annotated[orm.Session, Depends(get_rw_session)],
):
    origin = api_admin_assign_one_bib.__name__
    player_in_db = session.get(PlayerInDB, licence_no)

    if player_in_db is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    if player_in_db.bib_no is not None:
        raise ae.BibConflictError(
            origin=origin,
            error_message=ae.THIS_BIB_ALREADY_ASSIGNED_MESSAGE,
            payload={"licenceNo": licence_no, "bibNo": player_in_db.bib_no},
        )

    if session.scalars(select(distinct(PlayerInDB.bib_no))).all() == [None]:
        raise ae.BibConflictError(
            origin=origin,
            error_message=ae.NO_BIBS_ASSIGNED_MESSAGE,
        )

    session.execute(
        text(
            "UPDATE players SET "
            "bib_no = (SELECT MAX(bib_no) + 1 FROM players) "
            "WHERE licence_no = :licence_no;",
        ),
        {"licence_no": player_in_db.licence_no},
    )
    try:
        session.commit()
    except DBAPIError as e:
        session.rollback()
        raise ae.UnexpectedDBError(
            origin=origin,
            exception=e,
        )
    return Player.model_validate(session.get(PlayerInDB, licence_no))


@app.delete("/bibs")
@after_cutoff
def api_admin_reset_bibs(
    confirmation: str,
    session: Annotated[orm.Session, Depends(get_rw_session)],
):
    origin = api_admin_reset_bibs.__name__
    if confirmation != ae.RESET_BIBS_CONFIRMATION:
        raise ae.ConfirmationError(
            origin=origin,
            error_message=ae.RESET_BIBS_CONFIRMATION_MESSAGE,
        )
    try:
        session.execute(update(PlayerInDB).values(bib_no=None))
        session.commit()
    except DBAPIError as e:
        session.rollback()
        raise ae.UnexpectedDBError(
            origin=origin,
            exception=e,
        )

    return Response(status_code=HTTPStatus.NO_CONTENT)



@app.get("/players/all")
def api_admin_get_all_players(
    present_only: bool,
    session: Annotated[orm.Session, Depends(get_ro_session)],
) -> list[Player]:
    if present_only:
        query = (
            select(PlayerInDB)
            .distinct()
            .join(EntryInDB)
            .where(EntryInDB.marked_as_present.is_(True))
        )
    else:
        query = select(PlayerInDB)

    return [
        Player.model_validate(player)
        for player in session.scalars(query.order_by(PlayerInDB.licence_no)).all()
    ]


@app.get("/csv")
def api_admin_get_csv_zip(
    by_category: bool,
    session: Annotated[orm.Session, Depends(get_ro_session)],
):
    if by_category:
        players = []
        filenames = []
        for category in session.scalars(
            select(CategoryInDB).order_by(CategoryInDB.start_time),
        ).all():
            players.append(
                [
                    entry.player
                    for entry in sorted(
                        category.entries,
                        key=lambda e: e.registration_time,
                    )
                    if entry.marked_as_present is not False
                ][: category.max_players],
            )
            filenames.append(f"competiteurs_tableau_{category.category_id}.csv")
        zip_name = "competiteurs_par_tableaux"
    else:
        categories = session.scalars(select(CategoryInDB)).all()
        saturday_category_ids = [
            category.category_id
            for category in categories
            if category.start_time.weekday() == 5
        ]
        sunday_category_ids = [
            category.category_id
            for category in categories
            if category.start_time.weekday() == 6
        ]
        saturday_players = session.scalars(
            select(PlayerInDB)
            .distinct()
            .join(EntryInDB)
            .where(EntryInDB.category_id.in_(saturday_category_ids))
            .order_by(PlayerInDB.bib_no),
        ).all()
        sunday_players = session.scalars(
            select(PlayerInDB)
            .distinct()
            .join(EntryInDB)
            .where(EntryInDB.category_id.in_(sunday_category_ids))
            .order_by(PlayerInDB.bib_no),
        ).all()
        all_players = session.scalars(
            select(PlayerInDB).distinct().order_by(PlayerInDB.bib_no),
        ).all()

        players = [saturday_players, sunday_players, all_players]
        filenames = [
            "competiteurs_samedi.csv",
            "competiteurs_dimanche.csv",
            "competiteurs.csv",
        ]
        zip_name = "competiteurs_samedi_dimanche"

    return create_zip_file(filenames, players, zip_name)


def create_zip_file(filenames: list[str], players: list[list], zip_name: str):
    zip_file = BytesIO()

    def player_str(player_object):
        return (
            f"{player_object.bib_no},{player_object.licence_no},"
            f"{player_object.last_name},{player_object.first_name},"
            f"{player_object.nb_points},{player_object.club}\n"
        )

    with ZipFile(zip_file, "w") as zip_zip:
        for filename, player_list in zip(filenames, players):
            content = ["N° dossard, N° licence, Nom, Prénom, Points, Club\n"]
            content.extend(player_str(player) for player in player_list)
            zip_zip.writestr(
                filename,
                "".join(content),
            )

    zip_file.seek(0)
    return Response(
        zip_file.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment;filename={zip_name}.zip",
        },
    )
