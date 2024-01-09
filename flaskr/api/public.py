from collections import Counter
from datetime import datetime
from http import HTTPStatus
from json import loads

from flask import Blueprint, request, jsonify
from sqlalchemy import select, text, or_
from sqlalchemy.exc import DBAPIError
from marshmallow import ValidationError

from flaskr.api.marshmallow_schemas import (
    CategorySchema,
    EntrySchema,
    PlayerSchema,
    CategoryIdsSchema,
)
from flaskr.api.db import (
    Session,
    Category,
    Player,
    get_player_not_found_error,
    app_info,
)
from flaskr.api.fftt_api import get_player_fftt

public_api_bp = Blueprint("public_api", __name__, url_prefix="/api/public")

c_schema = CategorySchema()
e_schema = EntrySchema()
p_schema = PlayerSchema()


@public_api_bp.route("/categories", methods=["GET"])
def api_get_categories():
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
def api_add_player():
    if datetime.now() > app_info.registration_cutoff:
        return (
            jsonify(
                error="Public registration is closed.",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    p_schema.reset()
    try:
        player = p_schema.load(request.json)
    except ValidationError as e:
        return jsonify(error=e.messages), HTTPStatus.BAD_REQUEST

    with Session() as session:
        try:
            session.add(player)
            session.commit()
            return jsonify(p_schema.dump(player)), HTTPStatus.CREATED
        except DBAPIError:
            session.rollback()
            return (
                jsonify(
                    error="A player with this licence already exists in the database. "
                    "Player was not added.",
                ),
                HTTPStatus.BAD_REQUEST,
            )


@public_api_bp.route("/players/<int:licence_no>", methods=["GET"])
def api_get_player(licence_no):
    with Session() as session:
        if session.get(Player, licence_no) is not None:
            return (
                jsonify(
                    {
                        "PLAYER_ALREADY_REGISTERED_ERROR": f"Player with "
                        f"licence no {licence_no} is already registered",
                    },
                ),
                HTTPStatus.BAD_REQUEST,
            )

    db_only = request.args.get("db_only", False, loads) is True
    if db_only:
        return (
            jsonify(get_player_not_found_error(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )

    player_dict = get_player_fftt(licence_no)
    if player_dict is None:
        return (
            jsonify(get_player_not_found_error(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )
    return jsonify(player_dict), HTTPStatus.OK


@public_api_bp.route("/entries/<int:licence_no>", methods=["GET"])
def api_get_entries(licence_no):
    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            return (
                jsonify(
                    get_player_not_found_error(licence_no),
                ),
                HTTPStatus.BAD_REQUEST,
            )

        e_schema.reset(many=True)
        e_schema.context["include_category_info"] = True
        return jsonify(e_schema.dump(player.entries)), HTTPStatus.OK


@public_api_bp.route("/entries/<int:licence_no>", methods=["POST"])
def api_register_entries(licence_no):
    if datetime.now() > app_info.registration_cutoff:
        return (
            jsonify(
                error="Public registration is closed.",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    v_schema = CategoryIdsSchema()
    if error := v_schema.validate(request.json):
        return jsonify(error=error), HTTPStatus.BAD_REQUEST

    category_ids = request.json["categoryIds"]

    if not category_ids:
        return (
            jsonify(error="No categories to register entries in were sent."),
            HTTPStatus.BAD_REQUEST,
        )

    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            return (
                jsonify(
                    get_player_not_found_error(licence_no),
                ),
                HTTPStatus.BAD_REQUEST,
            )

        if nonexisting_category_ids := set(category_ids).difference(
            session.scalars(select(Category.category_id)),
        ):
            return (
                jsonify(
                    error=f"No categories with the following categoryIds "
                    f"{sorted(nonexisting_category_ids)} exist in the database",
                ),
                HTTPStatus.BAD_REQUEST,
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
            return (
                jsonify(
                    error=f"Tried to register some entries violating either gender or "
                    f"points conditions: {violations}",
                ),
                HTTPStatus.BAD_REQUEST,
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

        try:
            if (
                max(
                    Counter(
                        [
                            category.start_time.date()
                            for category in categories_including_previous_registrations
                        ],
                    ).values(),
                )
                > app_info.max_entries_per_day
            ):
                return (
                    jsonify(
                        error="Tried to register in too "
                        "many categories on the same day.",
                    ),
                    HTTPStatus.BAD_REQUEST,
                )
        except Exception as e:
            return (
                jsonify(error=f"Unexpected error: {e}"),
                HTTPStatus.CREATED,
            )
        temp_dicts = [
            {"categoryId": category_id, "licenceNo": licence_no}
            for category_id in category_ids
        ]

        query_str = (
            "INSERT INTO entries (category_id, licence_no, color) "
            "VALUES (:categoryId, :licenceNo, "
            "(SELECT color FROM categories WHERE category_id = :categoryId)) "
            "ON CONFLICT (category_id, licence_no) DO NOTHING;"
        )
        stmt = text(query_str)

        try:
            session.execute(stmt, temp_dicts)
            session.commit()
            p_schema.reset()
            p_schema.context["include_entries"] = True
            return jsonify(p_schema.dump(player)), HTTPStatus.CREATED
        except DBAPIError:
            session.rollback()
            return (
                jsonify(
                    error="One or several potential entries violate color constraint.",
                ),
                HTTPStatus.BAD_REQUEST,
            )
