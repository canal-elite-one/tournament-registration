from http import HTTPStatus
from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError

from flaskr.db import (
    session,
    Category,
    Player,
    get_player_not_found_error,
    CategorySchema,
    PlayerSchema,
    Entry,
    app_info,
)
from flaskr.api_input_schemas import MakePaymentSchema, CategoryIdsSchema
from sqlalchemy import delete, select, text, func, update, distinct
from sqlalchemy.exc import DBAPIError
from json import loads

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/categories", methods=["POST"])
def api_admin_set_categories():
    """
    Expects a jsonified list of dicts in the "categories" field of the json that can be
    passed unpacked to the category constructor. Don't forget to cast datetime types
    to some parsable string.
    """

    c_schema = CategorySchema(many=True)
    try:
        categories = c_schema.load(request.json)
    except ValidationError as e:
        return jsonify(error=e.messages), HTTPStatus.BAD_REQUEST

    try:
        session.execute(delete(Category))
    except DBAPIError:
        return (
            jsonify(
                error="Tried to reset categories while "
                "registration has already started.",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        for category in categories:
            session.add(category)
        session.commit()
        app_info.registration_cutoff()
        return (
            jsonify(
                c_schema.dump(
                    session.scalars(
                        select(Category).order_by(Category.start_time),
                    ).all(),
                ),
            ),
            HTTPStatus.CREATED,
        )
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@api_bp.route("/pay/<int:licence_no>", methods=["PUT"])
def api_admin_make_payment(licence_no):
    """
    Requires both a 'categoryIds' and a 'totalActualPaid' field in json.
    For each category_id, will update entry.marked_as_paid to True.
    Will update player.total_actual_paid to value of 'totalActualPaid'.
    Idempotent.

    Will return BAD_REQUEST (and not change anything db-side) for:
    - nonexisting licence_no.
    - category_ids that either do not exist in db or the player is not registered for.
    - WARNING: the corresponding entry is not marked_as_present = True.
    - WARNING: if totalActualPaid > sum of the fees required
        to pay for all entries with marked_as_present=True, or negative.
    This last 400 is to enforce the fact that a player can never pay more
    than the entries he has showed up for.
    """

    v_schema = MakePaymentSchema()
    if error := v_schema.validate(request.json):
        return jsonify(error=error), HTTPStatus.BAD_REQUEST

    if (player := session.get(Player, licence_no)) is None:
        return jsonify(get_player_not_found_error(licence_no)), HTTPStatus.BAD_REQUEST

    ids_to_pay = set(request.json["categoryIds"])

    if nonexisting_unregistered_nonpresent_categories := ids_to_pay.difference(
        entry.category_id for entry in player.present_entries()
    ):
        return (
            jsonify(
                error=f"Tried to pay the fee for some categories which "
                f"either did not exist, the player was not "
                f"registered for, or was not marked present: "
                f"{sorted(nonexisting_unregistered_nonpresent_categories)}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    for entry in player.present_entries():
        if entry.category_id in ids_to_pay:
            entry.marked_as_paid = True

    if player.current_required_payment() < request.json["totalActualPaid"]:
        session.rollback()
        return (
            jsonify(
                error="The 'totalActualPaid' field is higher than what the player must "
                "currently pay for all categories he is marked as present",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    player.total_actual_paid = request.json["totalActualPaid"]

    session.commit()
    p_schema = PlayerSchema()
    p_schema.context["include_entries"] = True
    return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/entries/<int:licence_no>", methods=["DELETE"])
def api_admin_delete_entries(licence_no):
    v_schema = CategoryIdsSchema()
    if error := v_schema.validate(request.json):
        return jsonify(error=error), HTTPStatus.BAD_REQUEST

    category_ids = request.json["categoryIds"]

    player = session.get(Player, licence_no)
    if player is None:
        return jsonify(get_player_not_found_error(licence_no)), HTTPStatus.BAD_REQUEST

    if unregistered_category_ids := set(category_ids).difference(
        entry.category_id for entry in player.entries
    ):
        return (
            jsonify(
                error=f"Tried to delete some entries which were not registered or "
                f"even for nonexisting categories: "
                f"{sorted(unregistered_category_ids)}.",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        session.execute(
            delete(Entry).where(
                Entry.licence_no == licence_no,
                Entry.category_id.in_(category_ids),
            ),
        )
        session.commit()
        p_schema = PlayerSchema()
        p_schema.context["include_entries"] = True
        return jsonify(p_schema.dump(player)), HTTPStatus.OK

    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@api_bp.route("/players/<int:licence_no>", methods=["DELETE"])
def api_admin_delete_player(licence_no):
    player = session.get(Player, licence_no)
    if player is None:
        return (
            jsonify(get_player_not_found_error(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        session.delete(player)
        session.commit()
        return Response(status=HTTPStatus.NO_CONTENT)
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@api_bp.route("/present/<int:licence_no>", methods=["PUT"])
def api_admin_mark_present(licence_no):
    """
    Expects json fields "categoryIdsToMark" and "categoryIdsToUnmark"
    with a list of categoryIds in each.
    For each category_id in the fields, will update value of
    player.marked_as_present to True/False,
    depending on which field it is in. Idempotent.

    Additionally, this is the only way to unpay an entry:
    It is assumed that the only valid transitions paid=True -> paid=False
    are of the form paid=True, present=True -> paid=False, present=False.
    The case paid=True, present=False -> Any is already prevented by hypothesis,
    but this endpoint (and the lack of unpay functionality for api_admin_make_payment)
    prevents paid=True, present=True -> paid=False, present=True.
    Furthermore, if player.total_actual_paid > player.current_required_payment()
    after unmarking some entries, then total_actual_paid is reduced to
    enforce inequality constraint.

    Returns BAD_REQUEST for:
    - nonexisting licence_no,
    - nonexisting and/or unregistered category_ids
    - nonempty intersection between the two fields,
    """
    player = session.get(Player, licence_no)
    if player is None:
        return (
            jsonify(get_player_not_found_error(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )

    ids_to_mark = set(request.json.get("categoryIdsToMark", []))
    ids_to_unmark = set(request.json.get("categoryIdsToUnmark", []))
    all_ids_to_update = ids_to_mark.union(ids_to_unmark)

    if unregistered_nonexisting_categories := all_ids_to_update.difference(
        entry.category_id for entry in player.entries
    ):
        return (
            jsonify(
                error=f"Tried to mark/unmark player for categories which he was not "
                f"registered for or even non_existing catgories"
                f": {sorted(unregistered_nonexisting_categories)}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    if present_in_both := ids_to_mark.intersection(ids_to_unmark):
        return (
            jsonify(
                error=f"Tried to mark and unmark player "
                f"as present for same categories: {sorted(present_in_both)}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    for entry in player.entries:
        if entry.category_id in all_ids_to_update:
            entry.marked_as_present = entry.category_id in ids_to_mark
            entry.marked_as_paid = (
                entry.marked_as_paid and entry.category_id not in ids_to_unmark
            )

    player.total_actual_paid = min(
        player.current_required_payment(),
        player.total_actual_paid,
    )

    session.commit()

    p_schema = PlayerSchema()
    p_schema.context["include_entries"] = True
    return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/bibs", methods=["POST"])
def api_admin_assign_all_bibs():
    if session.scalars(select(distinct(Player.bib_no))).all() != [None]:
        return (
            jsonify(
                error="Some bib numbers are already assigned. Either "
                "assign remaining bib_nos one by one, or reset bib_nos.",
            ),
            HTTPStatus.CONFLICT,
        )
    licence_nos = session.scalars(
        select(Player.licence_no)
        .join_from(Player, Entry)
        .join(Category)
        .group_by(Player.licence_no)
        .order_by(func.min(Category.start_time), Player.licence_no),
    )
    assigned_bib_nos = [
        {"licence_no": licence_no, "bib_no": (i + 1)}
        for i, licence_no in enumerate(licence_nos)
    ]
    session.execute(update(Player), assigned_bib_nos)
    session.commit()
    return jsonify(assignedBibs=assigned_bib_nos), HTTPStatus.OK


@api_bp.route("/bibs/<int:licence_no>", methods=["PUT"])
def api_admin_assign_one_bib(licence_no):
    player = session.get(Player, licence_no)

    if player is None:
        return (
            jsonify(get_player_not_found_error(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )

    if player.bib_no is not None:
        return (
            jsonify(error="This player already has a bib assigned."),
            HTTPStatus.CONFLICT,
        )

    if session.scalars(select(distinct(Player.bib_no))).all() == [None]:
        return (
            jsonify(
                error="Cannot assign bib numbers manually "
                "before having assigned them in bulk",
            ),
            HTTPStatus.CONFLICT,
        )

    session.execute(
        text(
            "UPDATE players SET "
            "bib_no = (SELECT MAX(bib_no) + 1 FROM players) "
            "WHERE licence_no = :licence_no;",
        ),
        {"licence_no": player.licence_no},
    )
    session.commit()
    p_schema = PlayerSchema()
    return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/bibs", methods=["DELETE"])
def api_admin_reset_bibs():
    confirmation = request.json.get("confirmation", None)
    if confirmation != "Je suis sur! J'ai appelé Céline!":
        return (
            jsonify(error="Missing or incorrect confirmation message."),
            HTTPStatus.FORBIDDEN,
        )
    session.execute(update(Player).values(bib_no=None))
    session.commit()
    return Response(status=HTTPStatus.NO_CONTENT)


@api_bp.route("/by_category", methods=["GET"])
def api_admin_get_players_by_category():
    present_only = request.args.get("present_only", False, loads) is True
    c_schema = CategorySchema(many=True)
    c_schema.context["include_players"] = True
    c_schema.context["present_only"] = present_only

    categories = session.scalars(select(Category).order_by(Category.start_time)).all()

    return jsonify(c_schema.dump(categories)), HTTPStatus.OK


@api_bp.route("/all_players", methods=["GET"])
def api_admin_get_all_players():
    present_only = request.args.get("present_only", False, loads) is True

    if present_only:
        query = (
            select(Player)
            .distinct()
            .join(Entry)
            .where(Entry.marked_as_present.is_(True))
        )
    else:
        query = select(Player)

    p_schema = PlayerSchema(many=True)
    p_schema.context["include_entries"] = True

    return jsonify(players=p_schema.dump(session.scalars(query).all())), HTTPStatus.OK


@api_bp.route("/categories", methods=["GET"])
def api_get_categories():
    return (
        jsonify(
            CategorySchema(many=True).dump(
                session.scalars(select(Category).order_by(Category.start_time)).all(),
            ),
        ),
        HTTPStatus.OK,
    )


@api_bp.route("/players", methods=["POST"])
def api_add_player():
    p_schema = PlayerSchema()
    try:
        player = p_schema.load(request.json)
    except ValidationError as e:
        return jsonify(error=e.messages), HTTPStatus.BAD_REQUEST

    try:
        session.add(player)
        session.commit()
        return p_schema.dump(player), HTTPStatus.CREATED
    except DBAPIError:
        session.rollback()
        return (
            jsonify(
                error="A player with this licence already exists in the database. "
                "Player was not added.",
            ),
            HTTPStatus.BAD_REQUEST,
        )


@api_bp.route("/players/<int:licence_no>", methods=["GET"])
def api_get_player(licence_no):
    player = session.get(Player, licence_no)
    if player is None:
        return jsonify(player=None, registeredEntries=[]), HTTPStatus.OK

    p_schema = PlayerSchema()
    p_schema.context["include_entries"] = True
    return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/entries/<int:licence_no>", methods=["POST"])
def api_register_entries(licence_no):
    v_schema = CategoryIdsSchema()
    if error := v_schema.validate(request.json):
        return jsonify(error=error), HTTPStatus.BAD_REQUEST

    category_ids = request.json["categoryIds"]

    if not category_ids:
        return (
            jsonify(error="No categories to register entries in were sent."),
            HTTPStatus.BAD_REQUEST,
        )

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
        p_schema = PlayerSchema()
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
