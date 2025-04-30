from io import BytesIO
from http import HTTPStatus
from zipfile import ZipFile
from typing import Annotated


from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, distinct, func, update, text
from sqlalchemy import orm
from sqlalchemy.exc import DBAPIError

from apis.shared.db import (
    CategoryInDB,
    PlayerInDB,
    EntryInDB,
)
import apis.shared.api_errors as ae
from apis.shared.custom_decorators import after_cutoff
from apis.shared.models import (
    Player,
    AliasedBase,
)
from apis.shared.dependencies import get_rw_session, get_ro_session

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
