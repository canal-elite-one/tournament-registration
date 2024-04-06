from collections import Counter
from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from shared.api.marshmallow_schemas import (
    CategorySchema,
    EntrySchema,
    PlayerSchema,
    CategoryIdsSchema,
    ContactInfoSchema,
)
from shared.api.db import (
    Session,
    Category,
    Player,
)
from shared.api.fftt_api import get_player_fftt
from shared.api.custom_decorators import during_registration, after_registration_start
import shared.api.api_errors as ae

public_api_bp = Blueprint("public_api", __name__, url_prefix="/api/public")

c_schema = CategorySchema()
e_schema = EntrySchema()
p_schema = PlayerSchema()


@public_api_bp.route("/categories", methods=["GET"])
@during_registration
def api_public_get_categories():
    c_schema.reset(many=True)
    with Session() as session:
        return (
            jsonify(
                c_schema.dump(
                    session.scalars(
                        select(Category).order_by(Category.start_time),
                    ).all(),
                ),
            ),
            HTTPStatus.OK,
        )


@public_api_bp.route("/players/<licence_no>", methods=["POST"])
@during_registration
def api_public_add_player(licence_no):
    origin = api_public_add_player.__name__
    v_schema = ContactInfoSchema()

    contact_info_dict = request.json

    if error := v_schema.validate(contact_info_dict):
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.PLAYER_CONTACT_FORMAT_MESSAGE,
            payload=error,
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
        raise ae.FFTTPlayerNotFoundError(origin=origin, licence_no=licence_no)

    player.email = contact_info_dict["email"]
    player.phone = contact_info_dict["phone"]
    player.total_actual_paid = 0

    with Session() as session:
        try:
            session.add(player)
            session.commit()
            return jsonify(p_schema.dump(player)), HTTPStatus.CREATED
        except DBAPIError:
            session.rollback()
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.DUPLICATE_PLAYER_MESSAGE,
                payload={"licenceNo": player.licence_no},
            )


@public_api_bp.route("/players/<licence_no>", methods=["GET"])
@during_registration
def api_public_get_player(licence_no):
    origin = api_public_get_player.__name__
    with Session() as session:
        if session.get(Player, licence_no) is not None:
            raise ae.PlayerAlreadyRegisteredError(
                origin=origin,
                error_message=ae.PLAYER_ALREADY_REGISTERED_MESSAGE,
                payload={"licenceNo": licence_no},
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
        raise ae.PlayerNotFoundError(origin=origin, licence_no=licence_no)

    player.total_actual_paid = 0

    p_schema.reset()

    return jsonify(p_schema.dump(player)), HTTPStatus.OK


@public_api_bp.route("/entries/<licence_no>", methods=["GET"])
@after_registration_start
def api_public_get_entries(licence_no):
    origin = api_public_get_entries.__name__
    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        e_schema.reset(many=True, include_category_info=True)
        return jsonify(e_schema.dump(player.entries)), HTTPStatus.OK


@public_api_bp.route("/entries/<licence_no>", methods=["POST"])
@during_registration
def api_public_register_entries(licence_no):
    origin = api_public_register_entries.__name__
    v_schema = CategoryIdsSchema()
    if error := v_schema.validate(request.json):
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.REGISTRATION_FORMAT_MESSAGE,
            payload=error,
        )

    category_ids = request.json["categoryIds"]

    if not category_ids:
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.REGISTRATION_MISSING_IDS_MESSAGE,
        )

    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        if nonexisting_category_ids := set(category_ids).difference(
                session.scalars(select(Category.category_id)),
        ):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
                payload={"categoryIds": sorted(nonexisting_category_ids)},
            )

        if player.entries:
            raise ae.PlayerAlreadyRegisteredError(
                origin=origin,
                error_message=ae.PLAYER_ALREADY_REGISTERED_MESSAGE,
                payload={"licenceNo": licence_no},
            )

        potential_categories = session.scalars(
            select(Category).where(Category.category_id.in_(category_ids)),
        ).all()

        # checks that if the player is female, they have to be registered to all
        # women-only categories on the same day for which they are registered to a category
        if player.gender == "F":
            days_with_entries = {category.start_time.date() for category in potential_categories}
            women_only_categories = session.scalars(
                select(Category)
                .where(Category.women_only.is_(True)),
            ).all()

            for day in days_with_entries:
                unregistered_women_only_categories_on_day = [
                    category.category_id for category in women_only_categories if category.start_time.date() == day
                                                                      and category.category_id not in category_ids
                ]
                if unregistered_women_only_categories_on_day:
                    raise ae.InvalidDataError(
                        origin=origin,
                        error_message=ae.MANDATORY_WOMEN_ONLY_REGISTRATION_MESSAGE,
                        payload={"categoryIdsShouldRegister": unregistered_women_only_categories_on_day},
                    )

        violations = [
            category.category_id
            for category in potential_categories
            if not player.respects_gender_points_constraints(category)
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
                > current_app.config["MAX_ENTRIES_PER_DAY"] + (player.gender == "F")
        ):
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
            p_schema.reset(include_entries=True)
            return jsonify(p_schema.dump(player)), HTTPStatus.CREATED
        except DBAPIError:
            session.rollback()
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.COLOR_VIOLATION_MESSAGE,
            )
