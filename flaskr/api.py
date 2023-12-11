from http import HTTPStatus
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify, Response
from flaskr.db import (
    session,
    Category,
    Player,
    player_not_found_message,
    CategorySchema,
    PlayerSchema,
    Entry,
)
from sqlalchemy import delete, select, text, func, update, distinct
from sqlalchemy.exc import DBAPIError
from datetime import date
from json import loads

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/categories", methods=["POST"])
def api_admin_set_categories():
    """
    Expects a jsonified list of dicts in the "categories" field of the json that can be
    passed unpacked to the category constructor. Don't forget to cast datetime types
    to some parsable string.
    """

    if "categories" not in request.json:
        return (
            jsonify(
                error="json was missing 'categories' field. Categories were not set",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    schema = CategorySchema(many=True)
    try:
        categories = schema.load(request.json["categories"])
    except ValidationError as e:
        return (
            jsonify(
                error=f"Some category data was missing or wrongly formatted. "
                f"Categories were not set. {e}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    session.execute(delete(Category))

    try:
        for category in categories:
            session.add(category)
        session.commit()
        return (
            jsonify(
                schema.dump(
                    session.scalars(
                        select(Category).order_by(Category.start_time),
                    ).all(),
                ),
            ),
            HTTPStatus.CREATED,
        )
    except DBAPIError as e:
        session.rollback()
        return (
            jsonify(
                error=f"At least two categories have the same name. Categories "
                f"were not set. {e}",
            ),
            HTTPStatus.BAD_REQUEST,
        )


@api_bp.route("/pay/<int:licence_no>", methods=["PUT"])
def api_admin_make_payment(licence_no):
    """
    This endpoint allows admin user to register payments
    made by players, specifically:\n
    * For which categories did they pay
    * How much did they actually pay if they did not pay the exact amount
    to settle all entries marked as paid, both for this
    transaction and for the previous ones.

    It requires some attached json in the request,
     with the following fields:\n
    * For paying player identification, either a ``'licenceNo'``
    or both a ``'firstName'`` and ``'lastName'`` str fields.
     Will prioritise using ``'licenceNo'`` if present.\n
    * A ``'categoryIds'`` array field\n
    * Optionally, an ``'actualPaid'`` int field, representing
    the actual amount of money that has just changed hands.

    WARNING: If the ``'actualPaid'`` field is not present, the default
    behaviour is to assume the current payment was
    exactly enough to settle ALL entries marked as paid,
    including those in previous transactions, as opposed to only
    those for this transaction. In other words, the value of
    ``player.payment_diff`` will be reset to ``0``,
    with the actual amount paid this transaction assumed to be:
    ``settled_now['amount'] - player.payment_diff`` instead of just ``settled_now``
    """
    if "categoryIds" not in request.json:
        return (
            jsonify(error="Missing 'categoryIds' field in json."),
            HTTPStatus.BAD_REQUEST,
        )

    player = session.get(Player, licence_no)
    if player is None:
        return (
            jsonify(error=player_not_found_message(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )

    to_pay = set(request.json["categoryIds"])
    all_entries = {"amount": 0, "categoryIds": []}
    settled_previously = {"amount": 0, "categoryIds": []}
    settled_now = {"amount": 0, "categoryIds": []}
    left_to_settle = {"amount": 0, "categoryIds": []}
    duplicates = []

    for entry in sorted(player.entries, key=lambda x: x.category.start_time):
        cat = entry.category
        all_entries["amount"] += cat.entry_fee
        all_entries["categoryIds"].append(cat.category_id)
        if entry.marked_as_paid:
            if cat.category_id in to_pay:
                duplicates.append(cat.category_id)
            settled_previously["amount"] += cat.entry_fee
            settled_previously["categoryIds"].append(cat.category_id)
        elif cat.category_id in to_pay:
            settled_now["amount"] += cat.entry_fee
            settled_now["categoryIds"].append(cat.category_id)
            to_pay.remove(cat.category_id)
        else:
            left_to_settle["amount"] += cat.entry_fee
            left_to_settle["categoryIds"].append(cat.category_id)

    if duplicates:
        return (
            jsonify(
                error=f"Tried to make payment for some entries which were already "
                f"paid for: {duplicates}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    if to_pay:
        return (
            jsonify(
                error=f"Tried to pay the fee for some categories which did not exist, "
                f"or to which the player was not registered: {to_pay}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    actual_paid_now = request.json.get("actualPaid", None)
    if actual_paid_now is None:
        actual_paid_now = settled_now["amount"] - player.payment_diff
        player.payment_diff = 0
    else:
        player.payment_diff = (
            actual_paid_now - settled_now["amount"] + player.payment_diff
        )

    for category_id in settled_now["categoryIds"]:
        entry = session.get(Entry, (category_id, licence_no))
        entry.marked_as_paid = True
    session.commit()
    recap = {
        "actualPaidNow": actual_paid_now,
        "paymentDiff": player.payment_diff,
        "actualRemaining": left_to_settle["amount"] - player.payment_diff,
        "allEntries": all_entries,
        "settledPreviously": settled_previously,
        "settledNow": settled_now,
        "leftToPay": left_to_settle,
    }
    return jsonify(recap), HTTPStatus.OK


@api_bp.route("/entries/<int:licence_no>", methods=["DELETE"])
def api_admin_delete_entries(licence_no):
    if "categoryIds" not in request.json:
        return (
            jsonify(error="Missing 'categoryIds' field in json."),
            HTTPStatus.BAD_REQUEST,
        )
    category_ids = request.json["categoryIds"]

    player = session.get(Player, licence_no)
    if player is None:
        return (
            jsonify(error=player_not_found_message(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )

    if unregistered_category_ids := set(category_ids).difference(
        entry.category_id for entry in player.entries
    ):
        return (
            jsonify(
                error=f"Tried to delete some entries which were not registered or "
                f"even for nonexisting categories: {unregistered_category_ids}.",
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
        p_schema.context["with_entries_info"] = True
        return jsonify(p_schema.dump(player)), HTTPStatus.OK

    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@api_bp.route("/players/<int:licence_no>", methods=["DELETE"])
def api_admin_delete_player(licence_no):
    player = session.get(Player, licence_no)
    if player is None:
        return (
            jsonify(error=player_not_found_message(licence_no)),
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
    This endpoint allows admin to record whether a player was present
    for each entry that they are registered for.
    It expects a json payload with the following fields\n
    * either a ``licenceNo`` or both a ``firstName`` and ``lastName`` str fields\n
    * either a ``categoryIdsToMark``, a ``categoryIdsToUnmark``
    array fields, both, or none\n
    If either or both of the categoryIds field are present,
    the endpoint changes the ``marked_as_present`` column for
    each relevant entries accordingly,
    except if the intersection of both array is nonempty,
    in which case it return a BAD_REQUEST.\n
    If none is present, the default behaviour is to set the
    ``marked_as_present`` column to ``True``
    for entries which correspond to categories with a
    ``start_time`` of today .
    """
    player = session.get(Player, licence_no)
    if player is None:
        return (
            jsonify(error=player_not_found_message(licence_no)),
            HTTPStatus.BAD_REQUEST,
        )

    ids_to_mark = set(request.json.get("categoryIdsToMark", []))
    ids_to_unmark = set(request.json.get("categoryIdsToUnmark", []))
    if present_in_both := ids_to_mark.intersection(ids_to_unmark):
        return (
            jsonify(
                error=f"Tried to mark and unmark player "
                f"as present for same categories: {present_in_both}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    def to_mark(en):
        if ids_to_mark or ids_to_unmark:
            return en.category_id in ids_to_mark
        return en.category.start_time.date() == date.today()

    session.execute(
        update(Entry),
        [
            {
                "licence_no": licence_no,
                "category_id": entry.category_id,
                "marked_as_present": True,
            }
            for entry in player.entries
            if to_mark(entry)
        ],
    )

    session.execute(
        update(Entry),
        [
            {
                "licence_no": licence_no,
                "category_id": entry.category_id,
                "marked_as_present": False,
            }
            for entry in player.entries
            if entry.category_id in ids_to_unmark
        ],
    )

    session.commit()

    p_schema = PlayerSchema()
    p_schema.context["with_entries_info"] = True
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
            jsonify(error=player_not_found_message(licence_no)),
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
    schema = PlayerSchema()
    return jsonify(schema.dump(player)), HTTPStatus.OK


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
    p_schema = PlayerSchema(many=True)

    result = {}
    for cat_id in session.scalars(select(Category.category_id)):
        query = select(Player).join(Entry).where(Entry.category_id == cat_id)
        if present_only:
            query = query.where(Entry.marked_as_present.is_(True))
        result[cat_id] = p_schema.dump(session.scalars(query).all())

    return jsonify(result), HTTPStatus.OK


@api_bp.route("/all_players", methods=["GET"])
def api_admin_get_all_players():
    present_only = request.args.get("present_only", False, loads) is True
    schema = PlayerSchema(many=True)
    schema.context["with_entries_info"] = True

    if present_only:
        query = (
            select(Player)
            .distinct()
            .join(Entry)
            .where(Entry.marked_as_present.is_(True))
        )
    else:
        query = select(Player)

    return jsonify(players=schema.dump(session.scalars(query).all())), HTTPStatus.OK


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
    if "player" not in request.json:
        return (
            jsonify(error="json was missing 'player' field. Player was not added."),
            HTTPStatus.BAD_REQUEST,
        )

    schema = PlayerSchema()
    try:
        player = schema.load(request.json["player"])
    except ValidationError as e:
        return (
            jsonify(
                error=f"Some player data was missing or wrongly formatted. "
                f"Player was not added. {e}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        session.add(player)
        session.commit()
        return schema.dump(player), HTTPStatus.CREATED
    except DBAPIError as e:
        session.rollback()
        return (
            jsonify(
                error=f"A player with this licence already exists in the database. "
                f"Player was not added. {e}",
            ),
            HTTPStatus.BAD_REQUEST,
        )


@api_bp.route("/players/<int:licence_no>", methods=["GET"])
def api_get_player(licence_no):
    player = session.get(Player, licence_no)
    if player is None:
        return jsonify(player=None, registeredEntries=[]), HTTPStatus.OK

    p_schema = PlayerSchema()
    p_schema.context["with_entries_info"] = True
    return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/entries/<int:licence_no>", methods=["POST"])
def api_register_entries(licence_no):
    if "categoryIds" not in request.json:
        return (
            jsonify(
                error="Missing 'categoryIds' field in json.",
            ),
            HTTPStatus.BAD_REQUEST,
        )

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
                error=player_not_found_message(licence_no),
            ),
            HTTPStatus.BAD_REQUEST,
        )

    if nonexisting_category_ids := set(category_ids).difference(
        session.scalars(select(Category.category_id)),
    ):
        return (
            jsonify(
                error=f"No categories with the following categoryIds "
                f"{nonexisting_category_ids} exist in the database",
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
        p_schema.context["with_entries_info"] = True
        return jsonify(p_schema.dump(player)), HTTPStatus.CREATED
    except DBAPIError as e:
        session.rollback()
        return (
            jsonify(
                error=f"One or several potential entries violate color constraint. {e}",
            ),
            HTTPStatus.BAD_REQUEST,
        )
