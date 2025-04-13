from collections import Counter
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import select, text, orm
from sqlalchemy.exc import DBAPIError

from apis.shared.dependencies import get_ro_session, get_rw_session
from apis.email_sender import EmailSender
from apis.shared.db import CategoryInDB, PlayerInDB, Session
from apis.shared.fftt_api import get_player_fftt

import apis.shared.config as cfg
import apis.shared.api_errors as ae
from apis.shared.models import (
    Category,
    ContactInfo,
    Player,
    FfttPlayer,
    Entry,
    AliasedBase,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/players/{licence_no}", operation_id="add_player", status_code=201)
# @during_registration
async def api_public_add_player(
    licence_no: str,
    contact_info: ContactInfo,
    session: Annotated[orm.Session, Depends(get_rw_session)],
) -> Player:
    origin = api_public_add_player.__name__

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

    try:
        session.add(player.to_db())
        session.commit()
        return player
    except DBAPIError:
        session.rollback()
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.DUPLICATE_PLAYER_MESSAGE,
            payload={"licenceNo": player.licence_no},
        )


@app.get("/players/<licence_no>", operation_id="get_player")
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
) -> list[Entry]:
    origin = api_public_get_entries.__name__
    player_in_db = session.get(PlayerInDB, licence_no)
    if player_in_db is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    return [Entry.model_validate(entry_in_db) for entry_in_db in player_in_db.entries]


class RegisterEntriesBody(AliasedBase):
    category_ids: list[str]


@app.post("/entries/<licence_no>", operation_id="register_entries")
# @during_registration
async def api_public_register_entries(
    licence_no: str,
    category_ids: RegisterEntriesBody,
) -> Player:
    origin = api_public_register_entries.__name__
    category_ids = category_ids.category_ids

    with Session() as session:
        if not category_ids:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.REGISTRATION_MISSING_IDS_MESSAGE,
            )

        player_in_db = session.get(PlayerInDB, licence_no)
        if player_in_db is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        if nonexisting_category_ids := set(category_ids).difference(
            session.scalars(select(CategoryInDB.category_id)),
        ):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
                payload={"categoryIds": sorted(nonexisting_category_ids)},
            )

        if player_in_db.entries:
            raise ae.PlayerAlreadyRegisteredError(
                origin=origin,
                error_message=ae.PLAYER_ALREADY_REGISTERED_MESSAGE,
                payload={"licenceNo": licence_no},
            )

        potential_categories = session.scalars(
            select(CategoryInDB).where(CategoryInDB.category_id.in_(category_ids)),
        ).all()

        # checks that if the player is female, they have to be registered to all
        # women-only categories on the same day for which they are registered to a
        # category
        if player_in_db.gender == "F":
            days_with_entries = {
                category.start_time.date() for category in potential_categories
            }
            women_only_categories = session.scalars(
                select(CategoryInDB).where(CategoryInDB.women_only.is_(True)),
            ).all()

            for day in days_with_entries:
                unregistered_women_only_categories_on_day = [
                    category.category_id
                    for category in women_only_categories
                    if category.start_time.date() == day
                    and category.category_id not in category_ids
                ]
                if unregistered_women_only_categories_on_day:
                    raise ae.InvalidDataError(
                        origin=origin,
                        error_message=ae.MANDATORY_WOMEN_ONLY_REGISTRATION_MESSAGE,
                        payload={
                            "categoryIdsShouldRegister": unregistered_women_only_categories_on_day,  # noqa: E501
                        },
                    )

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

        if max(
            Counter(
                [category.start_time.date() for category in potential_categories],
            ).values(),
        ) > cfg.MAX_ENTRIES_PER_DAY + (player_in_db.gender == "F"):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.MAX_ENTRIES_PER_DAY_MESSAGE,
            )
        temp_dicts = [
            {
                "categoryId": category_id,
                "licenceNo": licence_no,
                "registrationTime": datetime.now().isoformat(),
            }
            for category_id in category_ids
        ]

        query_str = (
            "INSERT INTO entries (category_id, licence_no, color, registration_time) "
            "VALUES (:categoryId, :licenceNo, "
            "(SELECT color FROM categories WHERE category_id = :categoryId),"
            ":registrationTime) "
            "ON CONFLICT (category_id, licence_no) DO NOTHING;"
        )
        stmt = text(query_str)

    try:
        session.execute(stmt, temp_dicts)
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
            f""": <a href="{cfg.TOURNAMENT_URL}/public/deja_inscrit/{licence_no}">cliquer ici</a>.<br><br>"""  # noqa: E501
            f"Merci de votre participation et à bientôt !<br><br>"
            f"L'équipe USKB",
            subject="Confirmation Inscription Tournoi USKB",
        )

        return Player.model_validate(player_in_db)
