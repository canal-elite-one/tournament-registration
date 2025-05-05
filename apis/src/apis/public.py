import logging
from collections import Counter
from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import delete, select, orm
from sqlalchemy.exc import DBAPIError
from pydantic import Field
from starlette.responses import PlainTextResponse, Response

from apis.shared.dependencies import get_ro_session, get_rw_session
from apis.email_sender import EmailSender
from apis.shared.db import CategoryInDB, PlayerInDB, Session, EntryInDB, \
    is_before_cutoff
from apis.shared.fftt_api import get_player_fftt

import apis.shared.config as cfg
import apis.shared.api_errors as ae
from apis.shared.models import (
    AdminPlayer,
    Category,
    ContactInfo,
    EntryWithPlayer,
    Player,
    FfttPlayer,
    AliasedBase,
    EntryWithCategory,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ae.APIError, ae.handle_api_error)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"Validation error: {exc}")
    return PlainTextResponse(str(exc), status_code=400)


class CategoryResult(Category):
    entry_count: int
    present_entry_count: int
    current_fee: int


@app.get("/categories", operation_id="get_categories")
# @during_registration
async def api_public_get_categories(
    session: Annotated[orm.Session, Depends(get_ro_session)],
) -> list[CategoryResult]:
    return [
        CategoryResult(
            **Category.model_validate(category_in_db).model_dump(),
            entry_count=len(category_in_db.entries),
            present_entry_count=len(category_in_db.present_entries()),
            current_fee=category_in_db.current_fee(),
        )
        for category_in_db in session.scalars(
            select(CategoryInDB).order_by(CategoryInDB.start_time),
        )
    ]


@app.get(
    "/players/<licence_no>",
    operation_id="get_player",
    response_model=FfttPlayer,
    responses={
        404: {"model": ae.APIErrorModel, "description": "Player not found in FFTT API"},
        403: {"model": ae.APIErrorModel, "description": "Player already registered"},
        500: {"model": ae.APIErrorModel, "description": "Unexpected FFTT API error"},
    },
)
# @during_registration
async def api_public_get_player(
    licence_no: str,
    session: Annotated[orm.Session, Depends(get_ro_session)],
) -> FfttPlayer:
    origin = api_public_get_player.__name__
    if session.get(PlayerInDB, licence_no) is not None:
        raise ae.PlayerAlreadyRegisteredError(
            origin=origin,
            error_message=ae.PLAYER_ALREADY_REGISTERED_MESSAGE,
            payload={"licenceNo": licence_no},
        )

    try:
        fftt_player = get_player_fftt(licence_no)
    except ae.FFTTAPIError as e:
        raise ae.UnexpectedFFTTError(
            origin=origin,
            message=e.message,
            payload=e.payload,
        )

    if fftt_player is None:
        raise ae.PlayerNotFoundError(origin=origin, licence_no=licence_no)

    return fftt_player


@app.get("/entries/<licence_no>", operation_id="get_entries")
# @after_registration_start
async def api_public_get_entries(
    licence_no: str,
    session: Annotated[orm.Session, Depends(get_ro_session)],
) -> list[EntryWithCategory]:
    origin = api_public_get_entries.__name__
    player_in_db = session.get(PlayerInDB, licence_no)
    if player_in_db is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    return [
        EntryWithCategory.from_entry_in_db(entry_in_db)
        for entry_in_db in player_in_db.entries
    ]


class RegisterEntriesBody(AliasedBase):
    category_ids: list[str] = Field(min_length=1)
    contact_info: ContactInfo


class RegisterEntriesResponse(AliasedBase):
    amount_to_pay: int


@app.post(
    "/entries/<licence_no>",
    operation_id="register_entries",
    response_model=RegisterEntriesResponse,
    status_code=201,
    responses={
        400: {
            "model": ae.APIErrorModel,
            "description": "Invalid category IDs or constraint violation",
        },
        403: {"model": ae.APIErrorModel, "description": "Player not found"},
        404: {"model": ae.APIErrorModel, "description": "Player does not exist"},
        500: {"model": ae.APIErrorModel, "description": "Unexpected FFTT API error"},
    },
)
# @during_registration
async def api_public_register_entries(
    licence_no: str,
    register_body: RegisterEntriesBody,
) -> RegisterEntriesResponse:
    origin = api_public_register_entries.__name__
    category_ids = register_body.category_ids
    contact_info = register_body.contact_info

    with Session() as session:
        player_in_db = session.get(PlayerInDB, licence_no)
        if player_in_db is not None:
            raise ae.PlayerAlreadyRegisteredError(
                origin=origin,
                error_message=ae.PLAYER_ALREADY_REGISTERED_MESSAGE,
                payload={"licenceNo": licence_no},
            )

        try:
            fftt_player = get_player_fftt(licence_no)
        except ae.FFTTAPIError as e:
            raise ae.UnexpectedFFTTError(
                origin=origin,
                message=e.message,
                payload=e.payload,
            )

        if fftt_player is None:
            raise ae.FFTTPlayerNotFoundError(origin=origin, licence_no=licence_no)

        player = Player(
            **fftt_player.model_dump(),
            email=contact_info.email,
            phone=contact_info.phone,
            total_actual_paid=0,
        )

        player_in_db = player.to_db()

        session.add(player_in_db)

        if nonexisting_category_ids := set(category_ids).difference(
            session.scalars(select(CategoryInDB.category_id)),
        ):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
                payload={"categoryIds": sorted(nonexisting_category_ids)},
            )

        potential_categories = session.scalars(
            select(CategoryInDB).where(CategoryInDB.category_id.in_(category_ids)),
        ).all()

        violations = [
            category.category_id
            for category in potential_categories
            if not player_in_db.respects_gender_points_constraints(category)
        ]

        if violations:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.GENDER_POINTS_VIOLATION_MESSAGE,
                payload={"categoryIds": violations},
            )

        if (
            max(
                Counter(
                    [category.start_time.date() for category in potential_categories],
                ).values(),
            )
            > cfg.MAX_ENTRIES_PER_DAY
        ):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.MAX_ENTRIES_PER_DAY_MESSAGE,
            )

        for category_id in category_ids:
            category = session.get(CategoryInDB, category_id)
            if category is None:
                raise ae.InvalidDataError(
                    origin=origin,
                    error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
                    payload={"categoryIds": [category_id]},
                )
            entry = EntryInDB(
                category_id=category_id,
                licence_no=licence_no,
                color=category.color,
                registration_time=datetime.now(),
            )
            session.add(entry)

        try:
            session.commit()
        except DBAPIError:
            session.rollback()
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.COLOR_VIOLATION_MESSAGE,
            )

    with Session() as session:
        player_in_db: PlayerInDB = session.get(PlayerInDB, licence_no)

        if all(
            entry.rank()
            > int(
                entry.category.max_players
                * (1 + entry.category.overbooking_percentage / 100),
            )
            for entry in player_in_db.entries
        ):
            EmailSender(
                sender_email=cfg.USKB_EMAIL,
                password=cfg.USKB_EMAIL_PASSWORD,
            ).send_email(
                recipient=player_in_db.email,
                bcc=cfg.ADMIN_EMAILS,
                body=f"Bonjour {player_in_db.first_name},<br><br>"
                f"Votre inscription sur liste d'attente a bien été prise en compte.<br><br>"
                f"Pour trouver votre position sur liste d'attente "
                f""": <a href="{cfg.TOURNAMENT_URL}/joueur/{licence_no}/inscription">cliquer ici</a>.<br><br>"""  # noqa: E501
                 "Vous recevrez un email pour procéder au paiement des tableaux auxquels vous serez repêché.<br><br>"  # noqa: E501
                f"Merci de votre inscription et à bientôt !<br><br>"
                f"L'équipe USKB",
                subject="Confirmation liste d'attente Tournoi USKB 2025",
            )

        return RegisterEntriesResponse(
            amount_to_pay=sum(
                entry.category.current_fee()
                for entry in player_in_db.entries
                if not entry.marked_as_paid and entry.rank()
                <= int(
                    entry.category.max_players
                    * (1 + entry.category.overbooking_percentage / 100),
                )
            ),
        )


class PayBody(AliasedBase):
    amount: int


@app.post("/pay/<licence_no>", operation_id="pay")
async def api_public_pay(
    licence_no: str,
    pay_body: PayBody,
    session: Annotated[orm.Session, Depends(get_rw_session)],
) -> Player:
    origin = api_public_pay.__name__
    player_in_db = session.get(PlayerInDB, licence_no)
    if player_in_db is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    player_in_db.total_actual_paid += pay_body.amount
    player = Player.model_validate(player_in_db)

    marked_as_paid_amount = 0
    for entry in player_in_db.entries:
        if not entry.is_in_waiting_list() and not entry.marked_as_paid:
            marked_as_paid_amount += entry.fee()
            entry.marked_as_paid = True

    if (pay_body.amount - marked_as_paid_amount) != 0:
        entries_total_not_in_waiting_list = sum(
            entry.fee()
            for entry in player_in_db.entries
            if not entry.is_in_waiting_list()
        )

        error_message = (
            f"Montant payé incohérent pour {player.licence_no}.<br>"
            f"Montant payé cette fois-ci: {pay_body.amount}<br>"
            f"Somme des inscriptions payées cette fois-ci: {marked_as_paid_amount}<br>"
            f"Montant total payé: {player.total_actual_paid}<br>"
            f"Coût total des tableaux principaux: {entries_total_not_in_waiting_list}<br>"
        )

        logging.error(f"Mark as paid error for {licence_no}:" + error_message)

        EmailSender(
            sender_email=cfg.USKB_EMAIL,
            password=cfg.USKB_EMAIL_PASSWORD,
        ).send_email(
            recipient=cfg.ADMIN_EMAILS[0],
            body=error_message,
            subject=f"Mark as paid error for {licence_no}",
            bcc=[],
        )
    session.commit()

    if marked_as_paid_amount > 0:
        EmailSender(
            sender_email=cfg.USKB_EMAIL,
            password=cfg.USKB_EMAIL_PASSWORD,
        ).send_email(
            recipient=player.email,
            bcc=cfg.ADMIN_EMAILS,
            body=f"Bonjour {player.first_name},<br><br>"
            f"Votre inscription a bien été prise en compte.<br><br>"
            f"Pour consulter les tableaux dans lesquels vous êtes inscrit(e) "
            f""": <a href="{cfg.TOURNAMENT_URL}/joueur/{licence_no}/inscription">cliquer ici</a>.<br><br>"""  # noqa: E501
            f"Merci de votre participation et à bientôt !<br><br>"
            f"L'équipe USKB",
            subject="Confirmation Inscription Tournoi USKB 2025",
        )
    return player


class SetCategoryInput(AliasedBase):
    categories: list[Category]


class SetCategoryResponse(AliasedBase):
    message: str

@app.post(
    "/admin/categories",
    operation_id="set_categories",
    response_model=SetCategoryResponse,
    status_code=201,
    responses={
        400: {
            "model": ae.APIErrorModel,
            "description": "Invalid category data",
        },
        500: {"model": ae.APIErrorModel, "description": "Unexpected error"},
    },
)
async def api_admin_set_categories(
    params: SetCategoryInput,
    session: Annotated[orm.Session, Depends(get_rw_session)],
) -> SetCategoryResponse:
    """
    Expects a jsonified list of dicts in the "categories" field of the json that can be
    passed unpacked to the category constructor. Don't forget to cast datetime types
    to some parsable string.
    """
    origin = api_admin_set_categories.__name__
    try:
        session.execute(delete(CategoryInDB))
    except DBAPIError:
        session.rollback()
        raise ae.RegistrationCutoffError(
            origin=origin,
            error_message=ae.RegistrationMessages.STARTED,
        )

    try:
        for category in params.categories:
            session.add(category.to_category_in_db())
        session.commit()

        return SetCategoryResponse(message="Successfully set categories")
    except DBAPIError as e:
        session.rollback()
        raise ae.UnexpectedDBError(
            origin=origin,
            exception=e,
        )


class GetAllPlayersResponse(AliasedBase):
    players: list[AdminPlayer]

@app.get(
    "/admin/players/all",
    operation_id="get_all_players",
    response_model=GetAllPlayersResponse,
)
def api_admin_get_all_players(
    present_only: bool,
    session: Annotated[orm.Session, Depends(get_ro_session)],
) -> GetAllPlayersResponse:
    if present_only:
        query = (
            select(PlayerInDB)
            .distinct()
            .join(EntryInDB)
            .where(EntryInDB.marked_as_present.is_(True))
        )
    else:
        query = select(PlayerInDB)

    results = []
    for player in session.scalars(query.order_by(PlayerInDB.licence_no)).all():
        entries_total_not_in_waiting_list = sum(
            entry.fee()
            for entry in player.entries
            if not entry.is_in_waiting_list() and entry.marked_as_present is not False
        )
        remaining_amount = entries_total_not_in_waiting_list - player.total_actual_paid
        results.append(
            AdminPlayer(
                **Player.model_validate(player).model_dump(),
                remaining_amount=remaining_amount,
            ),
        )

    return GetAllPlayersResponse(players=results)

class GetEntriesByCategoryResponse(AliasedBase):
    entries_by_category: dict[str, list[EntryWithPlayer]]

@app.get(
    "/admin/by_category",
    operation_id="get_entries_by_category",
    response_model=GetEntriesByCategoryResponse,
)
def api_admin_get_players_by_category(
    present_only: bool,
    session: Annotated[orm.Session, Depends(get_ro_session)],
) -> GetEntriesByCategoryResponse:
    categories = session.scalars(
        select(CategoryInDB).order_by(CategoryInDB.start_time),
    ).all()
    return GetEntriesByCategoryResponse(
        entries_by_category={
            category.category_id: [
                EntryWithPlayer.from_entry_in_db(entry)
                for entry in sorted(
                    category.entries,
                    key=lambda e: (e.marked_as_present is False, e.registration_time),
                )
                if present_only is False or entry.marked_as_present is not False
            ]
            for category in categories
        },
    )

class GetAdminPlayerResponse(AliasedBase):
    player: Player
    entries: list[EntryWithCategory]
    is_player_from_db: bool


@app.get(
    "/admin/players/<licence_no>",
    operation_id="get_admin_player_by_licence_no",
    response_model=GetAdminPlayerResponse,
)
def api_admin_get_player(
    licence_no: str, db_only: bool = False,
) -> GetAdminPlayerResponse:
    origin = api_admin_get_player.__name__
    with Session() as session:
        if (player := session.get(PlayerInDB, licence_no)) is not None:
            return GetAdminPlayerResponse(
                player=Player.model_validate(player),
                entries=[
                    EntryWithCategory.from_entry_in_db(entry)
                    for entry in player.entries
                ],
                is_player_from_db=True,
            )

    if db_only:
        raise ae.PlayerNotFoundError(
            origin=f"{origin}_db_only",
            licence_no=licence_no,
        )

    try:
        player = get_player_fftt(licence_no)
    except ae.FFTTAPIError as e:
        raise ae.UnexpectedFFTTError(
            origin=origin,
            message=e.message,
            payload=e.payload,
        )

    if player is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    return GetAdminPlayerResponse(
        player=Player.from_fftt_player(player),
        entries=[],
        is_player_from_db=False,
    )


@app.post("/admin/players/<licence_no>", operation_id="admin_add_player", response_model=Player)
def api_admin_add_player(
    licence_no: str,
    contact_info: ContactInfo,
    session: Annotated[orm.Session, Depends(get_rw_session)],
) -> Player:
    origin = api_admin_add_player.__name__

    try:
        fftt_player = get_player_fftt(licence_no)
    except ae.FFTTAPIError as e:
        raise ae.UnexpectedFFTTError(
            origin=origin,
            message=e.message,
            payload=e.payload,
        )

    if fftt_player is None:
        raise ae.FFTTPlayerNotFoundError(origin=origin, licence_no=licence_no)

    player = PlayerInDB(
        **fftt_player.model_dump(),
        **contact_info.model_dump(),
        total_actual_paid=0,
    )
    player_result = Player.model_validate(player)
    try:
        session.add(player)
        session.commit()
        return player_result
    except DBAPIError:
        session.rollback()
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.DUPLICATE_PLAYER_MESSAGE,
            payload={"licenceNo": player.licence_no},
        )


@app.patch(
    "/admin/players/<licence_no>",
    operation_id="admin_update_player",
    response_model=Player,
)
def api_admin_update_player(
    licence_no: str,
    contact_info: ContactInfo,
    session: Annotated[orm.Session, Depends(get_rw_session)],
) -> Player:
    origin = api_admin_add_player.__name__

    player = session.get(PlayerInDB, licence_no)
    # checks that the player exists in the database (not just in FFTT)
    if player is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    player.email = contact_info.email
    player.phone = contact_info.phone
    session.merge(player)
    return Player.model_validate(player)


class EntryInfo(AliasedBase):
    category_id: str
    marked_as_present: bool | None
    marked_as_paid: bool


@app.post("/admin/entries/<licence_no>", operation_id="admin_register_entries", response_model=Player)
def api_admin_register_entries(
    licence_no: str,
    entries: list[EntryInfo],
    total_actual_paid: int,
    session: Annotated[orm.Session, Depends(get_rw_session)],
) -> Player:
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
        actual_entry = EntryInDB(
            category_id=entry.category_id,
            licence_no=licence_no,
            color=category.color,
            marked_as_present=entry.marked_as_present,
            marked_as_paid=entry.marked_as_paid,
        )
        if entry.category_id not in old_entry_category_ids:
            actual_entry.registration_time = datetime.now()
            player.entries.append(actual_entry)
            category.entries.append(actual_entry)
        else:
            session.merge(actual_entry)

    player.total_actual_paid = total_actual_paid

    player_result = Player.model_validate(player)

    try:
        session.commit()
    except DBAPIError as e:
        session.rollback()
        raise ae.UnexpectedDBError(
            origin=origin,
            exception=e,
        )

    return player_result


@app.delete("/players/<licence_no>", operation_id="admin_delete_player", status_code=HTTPStatus.NO_CONTENT)
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
