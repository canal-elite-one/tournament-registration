from http import HTTPStatus
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify, Response
from flaskr.db import (
    session,
    Category,
    Player,
    CategorySchema,
    PlayerSchema,
    EntrySchema,
    Entry,
)
from sqlalchemy import delete, select, text, func, not_, update
from sqlalchemy.exc import DBAPIError
from datetime import date

bp = Blueprint("api", __name__, url_prefix="/api")


def find_player_by_name_or_licence(json_payload):
    if "licenceNo" not in json_payload and (
        "firstName" not in json_payload or "lastName" not in json_payload
    ):
        return {
            "is_valid": False,
            "error": "Missing 'licenceNo' and ('firstName' or 'lastName') fields "
            "in json.",
        }
    licence_no = json_payload.get("licenceNo", None)
    if licence_no is not None:
        player = session.scalar(select(Player).filter_by(licence_no=licence_no))
        if player is None:
            return {
                "is_valid": False,
                "error": f"No player with licence number {licence_no} exists in the "
                f"database. Search by name was not done as there was a "
                f"non-null 'licenceNo' field in json.",
            }
    else:
        first_name, last_name = json_payload["firstName"], json_payload["lastName"]
        player = session.scalar(
            select(Player).where(
                Player.first_name == first_name,
                Player.last_name == last_name,
            ),
        )
        if player is None:
            return {
                "is_valid": False,
                "error": f"No player named {first_name} {last_name} exists in "
                f"the database.",
            }
    return {"is_valid": True, "player": player}


@bp.route("/categories", methods=["POST"])
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
                categories=schema.dump(
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


@bp.route("/pay", methods=["PUT"])
def api_admin_make_payment():
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

    player_search = find_player_by_name_or_licence(request.json)
    if player_search["is_valid"]:
        player = player_search["player"]
    else:
        return jsonify(error=player_search["error"]), HTTPStatus.BAD_REQUEST

    player_entries = session.execute(
        select(Category.entry_fee, Category.category_id, Entry.marked_as_paid)
        .join_from(Category, Entry)
        .where(Entry.licence_no == player.licence_no),
    )

    to_pay = set(request.json["categoryIds"])
    all_entries = {"amount": 0, "categoryIds": []}
    settled_previously = {"amount": 0, "categoryIds": []}
    settled_now = {"amount": 0, "categoryIds": []}
    left_to_settle = {"amount": 0, "categoryIds": []}
    duplicates = []

    for entry_fee, category_id, paid in player_entries:
        all_entries["amount"] += entry_fee
        all_entries["categoryIds"].append(category_id)
        if paid:
            if category_id in to_pay:
                duplicates.append(category_id)
            settled_previously["amount"] += entry_fee
            settled_previously["categoryIds"].append(category_id)
        elif category_id in to_pay:
            settled_now["amount"] += entry_fee
            settled_now["categoryIds"].append(category_id)
            to_pay.remove(category_id)
        else:
            left_to_settle["amount"] += entry_fee
            left_to_settle["categoryIds"].append(category_id)

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
        entry = session.scalar(
            select(Entry).where(
                Entry.licence_no == player.licence_no,
                Entry.category_id == category_id,
            ),
        )
        entry.paid = True
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


@bp.route("/entries", methods=["DELETE"])
def api_admin_delete_entries():
    if "categoryIds" not in request.json:
        return (
            jsonify(error="Missing 'categoryIds' field in json."),
            HTTPStatus.BAD_REQUEST,
        )
    category_ids = request.json["categoryIds"]

    player_search = find_player_by_name_or_licence(request.json)
    if player_search["is_valid"]:
        licence_no = player_search["player"].licence_no
    else:
        return jsonify(error=player_search["error"]), HTTPStatus.BAD_REQUEST

    if unregistered_categories := set(category_ids).difference(
        session.scalars(
            select(Entry.category_id).where(Entry.licence_no == licence_no),
        ),
    ):
        return (
            jsonify(
                error=f"Tried to delete some entries which were not registered or "
                f"even for nonexisting categories: {unregistered_categories}.",
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
        e_schema = EntrySchema(many=True)
        # TODO: (cf db.PlayerSchema) make it so that p_schema.dump(player
        #  automatically generates all the data
        return (
            jsonify(
                remainingEntries=e_schema.dump(
                    session.scalars(
                        select(Entry).where(Entry.licence_no == licence_no),
                    ),
                ),
            ),
            HTTPStatus.OK,
        )
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@bp.route("/players", methods=["DELETE"])
def api_admin_delete_player():
    player_search = find_player_by_name_or_licence(request.json)
    if player_search["is_valid"]:
        licence_no = player_search["player"].licence_no
    else:
        return jsonify(error=player_search["error"]), HTTPStatus.BAD_REQUEST

    try:
        session.execute(delete(Entry).filter_by(licence_no=licence_no))
        session.execute(delete(Player).filter_by(licence_no=licence_no))
        session.commit()
        return Response(status=HTTPStatus.NO_CONTENT)
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@bp.route("/present", methods=["PUT"])
def api_admin_mark_present():
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
    player_search = find_player_by_name_or_licence(request.json)
    if player_search["is_valid"]:
        licence_no = player_search["player"].licence_no
    else:
        return jsonify(error=player_search["error"]), HTTPStatus.BAD_REQUEST

    ids_to_mark = request.json.get("categoryIdsToMark", [])
    ids_to_unmark = request.json.get("categoryIdsToUnmark", [])
    if present_in_both := set(ids_to_mark).intersection(ids_to_unmark):
        return (
            jsonify(
                error=f"Tried to mark and unmark player "
                f"as present for same categories: {present_in_both}",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    if not ids_to_mark and not ids_to_unmark:
        entries_to_mark = list(
            session.scalars(
                select(Entry)
                .join_from(Entry, Category)
                .where(
                    Entry.licence_no == licence_no,
                    func.date(Category.start_time) == date.today(),
                    not_(Entry.marked_as_present),
                )
                .order_by(Entry.category_id),
            ),
        )
    elif ids_to_mark:
        entries_to_mark = list(
            session.scalars(
                select(Entry)
                .where(
                    Entry.licence_no == licence_no,
                    Entry.category_id.in_(ids_to_mark),
                    not_(Entry.marked_as_present),
                )
                .order_by(Entry.category_id),
            ),
        )
    else:
        entries_to_mark = []

    for entry_to_mark in entries_to_mark:
        entry_to_mark.marked_as_present = True

    entries_to_unmark = list(
        session.scalars(
            select(Entry)
            .where(
                Entry.licence_no == licence_no,
                Entry.category_id.in_(ids_to_unmark),
                Entry.marked_as_present,
            )
            .order_by(Entry.category_id),
        )
        if ids_to_unmark
        else [],
    )
    for entry_to_unmark in entries_to_unmark:
        entry_to_unmark.marked_as_present = False

    session.commit()

    schema = EntrySchema(many=True)
    return (
        jsonify(
            marked=[entry.category_id for entry in entries_to_mark],
            unmarked=[entry.category_id for entry in entries_to_unmark],
            allEntries=schema.dump(
                session.scalars(
                    select(Entry)
                    .where(Entry.licence_no == licence_no)
                    .order_by(Entry.category_id),
                ),
            ),
        ),
        HTTPStatus.OK,
    )


@bp.route("/bibs", methods=["POST"])
def api_admin_assign_all_bibs():
    existing_bib_nos = session.scalars(
        select(Player.bib_no).group_by(Player.bib_no),
    ).all()
    if existing_bib_nos != [None]:
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


@bp.route("/categories", methods=["GET"])
def api_get_categories():
    return (
        jsonify(
            categories=CategorySchema(many=True).dump(
                session.scalars(select(Category).order_by(Category.start_time)),
            ),
        ),
        HTTPStatus.OK,
    )


@bp.route("/players", methods=["POST"])
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
    # TODO: try to do this as a subquery of an insert statement?

    player.bib_no = None

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


@bp.route("/players", methods=["GET"])
def api_get_player():
    if "licenceNo" not in request.json:
        return (
            jsonify(
                error="json was missing 'licenceNo' field. Could not retrieve "
                "player info.",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    licence_no = request.json["licenceNo"]

    player = session.scalar(select(Player).where(Player.licence_no == licence_no))
    if player is None:
        return jsonify(player=None, registeredEntries=[]), HTTPStatus.OK

    p_schema = PlayerSchema()
    e_schema = EntrySchema(many=True)
    # TODO: (cf db.PlayerSchema) make it so that p_schema.dump(player
    #  automatically generates all the data
    return (
        jsonify(
            player=p_schema.dump(player),
            registeredEntries=e_schema.dump(
                session.scalars(select(Entry).where(Entry.licence_no == licence_no)),
            ),
        ),
        HTTPStatus.OK,
    )


@bp.route("/entries", methods=["POST"])
def api_register_entries():
    if "licenceNo" not in request.json or "categoryIds" not in request.json:
        return (
            jsonify(
                error="Missing either 'licenceNo' or 'categoryIds' field in json.",
            ),
            HTTPStatus.BAD_REQUEST,
        )

    licence_no = request.json["licenceNo"]
    category_ids = request.json["categoryIds"]

    if not category_ids:
        return (
            jsonify(error="No categories to register entries in were sent."),
            HTTPStatus.BAD_REQUEST,
        )

    player = session.scalar(select(Player).filter_by(licence_no=licence_no))
    if player is None:
        return (
            jsonify(
                error=f"No player with licence number {licence_no} exists in the "
                f"database. Entry was not registered.",
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
        e_schema = EntrySchema(many=True)
        # TODO: (cf db.PlayerSchema) make it so that p_schema.dump(player
        #  automatically generates all the data
        return (
            jsonify(
                entries=e_schema.dump(
                    session.scalars(
                        select(Entry)
                        .where(Entry.licence_no == licence_no)
                        .order_by(Entry.category_id),
                    ),
                ),
            ),
            HTTPStatus.CREATED,
        )
    except DBAPIError as e:
        session.rollback()
        return (
            jsonify(
                error=f"One or several potential entries violate color constraint. {e}",
            ),
            HTTPStatus.BAD_REQUEST,
        )
