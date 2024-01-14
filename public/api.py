from collections import Counter
from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import select, text, or_
from sqlalchemy.exc import DBAPIError
from marshmallow import ValidationError

from shared.api.marshmallow_schemas import (
    CategorySchema,
    EntrySchema,
    PlayerSchema,
    CategoryIdsSchema,
)
from shared.api.db import (
    Session,
    Category,
    Player,
)
from shared.api.fftt_api import get_player_fftt
from shared.api.custom_decorators import before_cutoff
import shared.api.api_errors as ae

public_api_bp = Blueprint("public_api", __name__, url_prefix="/api/public")

c_schema = CategorySchema()
e_schema = EntrySchema()
p_schema = PlayerSchema()


@public_api_bp.route("/categories", methods=["GET"])
@before_cutoff
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


@public_api_bp.route("/players", methods=["POST"])
@before_cutoff
def api_public_add_player():
    origin = api_public_add_player.__name__
    p_schema.reset()
    try:
        player = p_schema.load(request.json)
    except ValidationError as e:
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.PLAYER_FORMAT_MESSAGE,
            payload=e.messages,
        )

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


@public_api_bp.route("/players/<int:licence_no>", methods=["GET"])
@before_cutoff
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
        player_dict = get_player_fftt(licence_no)
    except ae.FFTTAPIError as e:
        raise ae.UnexpectedFFTTError(origin=origin, payload=e.payload)

    if player_dict is None:
        raise ae.PlayerNotFoundError(origin=origin, licence_no=licence_no)

    return jsonify(player_dict), HTTPStatus.OK


@public_api_bp.route("/entries/<int:licence_no>", methods=["GET"])
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


@public_api_bp.route("/entries/<int:licence_no>", methods=["POST"])
@before_cutoff
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

        potential_categories = session.scalars(
            select(Category).where(Category.category_id.in_(category_ids)),
        )

        violations = []
        for category in potential_categories:
            if (
                (category.women_only and player.gender != "F")
                or (player.nb_points > category.max_points)
                or (player.nb_points < category.min_points)
            ):
                violations.append(category.category_id)
        if violations:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.GENDER_POINTS_VIOLATION_MESSAGE,
                payload={"categoryIds": violations},
            )

        categories_including_previous_registrations = session.scalars(
            select(Category).where(
                or_(
                    Category.category_id.in_(category_ids),
                    Category.category_id.in_(
                        [entry.category_id for entry in player.entries],
                    ),
                ),
            ),
        )

        if (
            max(
                Counter(
                    [
                        category.start_time.date()
                        for category in categories_including_previous_registrations
                    ],
                ).values(),
            )
            > current_app.config["MAX_ENTRIES_PER_DAY"]
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
