from collections import Counter
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import select, orm
from sqlalchemy.exc import DBAPIError
from pydantic import Field

from apis.shared.dependencies import get_ro_session, get_rw_session
from apis.email_sender import EmailSender
from apis.shared.db import CategoryInDB, PlayerInDB, Session, EntryInDB
from apis.shared.fftt_api import get_player_fftt

import apis.shared.config as cfg
import apis.shared.api_errors as ae
from apis.shared.models import (
    Category,
    ContactInfo,
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
        player_in_db = session.get(PlayerInDB, licence_no)

        is_on_waiting_list = any(
            entry.rank()
            > int(
                entry.category.max_players
                * (1 + entry.category.overbooking_percentage / 100),
            )
            for entry in player_in_db.entries
        )

        EmailSender(
            sender_email=cfg.USKB_EMAIL,
            password=cfg.USKB_EMAIL_PASSWORD,
        ).send_email(
            recipient=player_in_db.email,
            bcc=cfg.ADMIN_EMAILS,
            body=f"Bonjour {player_in_db.first_name},<br><br>"
            f"Votre inscription a bien été prise en compte.<br><br>"
            f"Pour consulter les tableaux dans lesquels vous êtes inscrit(e) "
            f"""{"ou trouver votre position sur liste d'attente " if is_on_waiting_list else ""}"""  # noqa: E501
            f""": <a href="{cfg.TOURNAMENT_URL}/joueur/{licence_no}/inscription">cliquer ici</a>.<br><br>"""  # noqa: E501
            f"Merci de votre participation et à bientôt !<br><br>"
            f"L'équipe USKB",
            subject="Confirmation Inscription Tournoi USKB 2025",
        )

        return RegisterEntriesResponse(
            amount_to_pay=sum(
                entry.category.current_fee()
                for entry in player_in_db.entries
                if entry.rank()
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
    session.commit()
    return player
