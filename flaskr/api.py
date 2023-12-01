from http import HTTPStatus
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify, Response
from flaskr.db import session, Category, Player, CategorySchema, PlayerSchema, EntrySchema, Entry
from sqlalchemy import delete, select, text
from sqlalchemy.exc import DBAPIError

bp = Blueprint("api", __name__, url_prefix="/api")


def find_player_by_name_or_licence(json_payload):
    if 'licenceNo' not in json_payload and ('firstName' not in json_payload or 'lastName' not in json_payload):
        return {"is_valid": False,
                "error": "Missing 'licenceNo' and ('firstName' or 'lastName') fields in json."}
    licence_no = json_payload.get('licenceNo', None)
    if licence_no is not None:
        if session.scalar(select(Player).filter_by(licence_no=licence_no)) is None:
            return {"is_valid": False,
                    "error": f"No player with licence number {licence_no} exists in the database. Search by name was not done as there was a non-null 'licenceNo' field in json."}
    else:
        first_name, last_name = json_payload['firstName'], json_payload['lastName']
        player = session.scalar(select(Player).where(Player.first_name == first_name,
                                                      Player.last_name == last_name))
        if player is None:
            return {"is_valid": False,
                    "error": f"No player named {first_name} {last_name} exists in the database."}
        else:
            licence_no = player.licence_no
    return {"is_valid": True, "licence_no": licence_no}


@bp.route("/categories", methods=["POST"])
def api_admin_set_categories():
    """
    Expects a jsonified list of dicts in the "categories" field of the json that can be passed unpacked to the
    category constructor. Don't forget to cast datetime types to some parsable string.
    """

    if 'categories' not in request.json:
        return jsonify(error=f"json was missing 'categories' field. Categories were not set"), HTTPStatus.BAD_REQUEST

    schema = CategorySchema(many=True)
    try:
        categories = schema.load(request.json['categories'])
    except ValidationError as e:
        return jsonify(
            error=f"Some category data was missing or wrongly formatted. Categories were not set. {e}"), HTTPStatus.BAD_REQUEST

    session.execute(delete(Category))

    try:
        for category in categories:
            session.add(category)
        session.commit()
        return jsonify(categories=
                       schema.dump(session.scalars(
                           select(Category).order_by(Category.start_time)).all())), HTTPStatus.CREATED
    except DBAPIError as e:
        session.rollback()
        return jsonify(
            error=f"At least two categories have the same name. Categories were not set. {e}"), HTTPStatus.BAD_REQUEST


@bp.route('/pay', methods=['PUT'])
def api_admin_make_payment():
    if 'categoryIds' not in request.json:
        return jsonify(error="Missing 'categoryIds' field in json."), HTTPStatus.BAD_REQUEST

    player_search = find_player_by_name_or_licence(request.json)
    if player_search['is_valid']:
        licence_no = player_search['licence_no']
    else:
        return jsonify(error=player_search['error']), HTTPStatus.BAD_REQUEST

    player_entries = session.execute(
        select(Category.entry_fee, Category.category_id, Entry.paid).join_from(Category, Entry).where(
            Entry.licence_no == licence_no))

    to_pay = set(request.json['categoryIds'])
    all_entries = {'amount': 0, 'categoryIds': []}
    previously_paid = {'amount': 0, 'categoryIds': []}
    paid_now = {'amount': 0, 'categoryIds': []}
    left_to_pay = {'amount': 0, 'categoryIds': []}
    duplicates = []

    for entry_fee, category_id, paid in player_entries:
        all_entries['amount'] += entry_fee
        all_entries['categoryIds'].append(category_id)
        if paid:
            if category_id in to_pay:
                duplicates.append(category_id)
            previously_paid['amount'] += entry_fee
            previously_paid['categoryIds'].append(category_id)
        elif category_id in to_pay:
            paid_now['amount'] += entry_fee
            paid_now['categoryIds'].append(category_id)
            to_pay.remove(category_id)
        else:
            left_to_pay['amount'] += entry_fee
            left_to_pay['categoryIds'].append(category_id)

    if duplicates:
        return jsonify(
            error=f'Tried to make payment for some entries which were already paid for: {duplicates}'), HTTPStatus.BAD_REQUEST

    if to_pay:
        return jsonify(
            error=f"Tried to pay the fee for some categories which did not exist, "
                  f"or to which the player was not registered: {to_pay}"), HTTPStatus.BAD_REQUEST

    for category_id in paid_now['categoryIds']:
        entry = session.scalar(
            select(Entry).where(Entry.licence_no == licence_no, Entry.category_id == category_id))
        entry.paid = True
    session.commit()
    recap = {'allEntries': all_entries, 'previouslyPaid': previously_paid, 'paidNow': paid_now,
             'leftToPay': left_to_pay}
    return jsonify(recap=recap), HTTPStatus.OK


@bp.route('/entries', methods=['DELETE'])
def api_admin_delete_entries():
    if 'categoryIds' not in request.json:
        return jsonify(error="Missing 'categoryIds' field in json."), HTTPStatus.BAD_REQUEST
    category_ids = request.json['categoryIds']

    player_search = find_player_by_name_or_licence(request.json)
    if player_search['is_valid']:
        licence_no = player_search['licence_no']
    else:
        return jsonify(error=player_search['error']), HTTPStatus.BAD_REQUEST

    if a := set(category_ids).difference(
            session.scalars(select(Entry.category_id).where(Entry.licence_no == licence_no))):
        return jsonify(
            error=f"Tried to delete some entries which were not registered "
                  f"or even for nonexisting categories: {a}."), HTTPStatus.BAD_REQUEST

    try:
        session.execute(delete(Entry).where(Entry.licence_no == licence_no,
                                              Entry.category_id.in_(category_ids)))
        session.commit()
        e_schema = EntrySchema(many=True)
        # TODO: (cf db.PlayerSchema) make it so that p_schema.dump(player automatically generates all the data
        return jsonify(remainingEntries=e_schema.dump(
            session.scalars(select(Entry).where(Entry.licence_no == licence_no)))), HTTPStatus.OK
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@bp.route('/players', methods=['DELETE'])
def api_admin_delete_player():
    player_search = find_player_by_name_or_licence(request.json)
    if player_search['is_valid']:
        licence_no = player_search['licence_no']
    else:
        return jsonify(error=player_search['error']), HTTPStatus.BAD_REQUEST

    try:
        session.execute(delete(Entry).filter_by(licence_no=licence_no))
        session.execute(delete(Player).filter_by(licence_no=licence_no))
        session.commit()
        return Response(status=HTTPStatus.NO_CONTENT)
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@bp.route('/categories', methods=['GET'])
def api_get_categories():
    return jsonify(categories=CategorySchema(many=True).dump(
        session.scalars(select(Category).order_by(Category.start_time)))), HTTPStatus.OK


@bp.route('/players', methods=['POST'])
def api_add_player():
    if 'player' not in request.json:
        return jsonify(error="json was missing 'player' field. Player was not added."), HTTPStatus.BAD_REQUEST

    schema = PlayerSchema()
    try:
        player = schema.load(request.json['player'])
    except ValidationError as e:
        # also triggers if 'bibNo' field is None instead of just not there
        return jsonify(
            error=f"Some player data was missing or wrongly formatted. Player was not added. {e}"), HTTPStatus.BAD_REQUEST
    # TODO: try to do this as a subquery of an insert statement?

    # query_str = \
    #     ("INSERT INTO players (category_id, licence_no, registration_time) "
    #      "VALUES (:categoryId, :licenceNo, :registrationTime, "
    #      "(SELECT min(a) "
    #      "FROM generate_series(1, (SELECT max(bib_no) + 1 FROM players)) AS a "
    #      "WHERE a NOT IN (SELECT bib_no FROM players)))"
    #      "ON CONFLICT (category_id, licence_no) DO NOTHING ;")
    # stmt = text(query_str)

    existing_bib_nos = session.scalars(select(Player.bib_no)).all()
    max_bib_no = max(existing_bib_nos or [0])
    next_bib_no = max_bib_no + 1 if max_bib_no == len(existing_bib_nos) else (
        min(set(range(1, max_bib_no + 1)) - set(existing_bib_nos)))
    player.bib_no = next_bib_no

    try:
        session.add(player)
        session.commit()
        return jsonify(player=schema.dump(player)), HTTPStatus.CREATED
    except DBAPIError as e:
        session.rollback()
        return jsonify(
            error=f"A player with this licence already exists in the database. Player was not added. {e}"), HTTPStatus.BAD_REQUEST


@bp.route('/players', methods=['GET'])
def api_get_player():
    if 'licenceNo' not in request.json:
        return jsonify(error="json was missing 'licenceNo' field. Could not retrieve player info."), HTTPStatus.BAD_REQUEST

    licence_no = request.json['licenceNo']

    player = session.scalar(select(Player).where(Player.licence_no == licence_no))
    if player is None:
        return jsonify(player=None, registeredEntries=[]), HTTPStatus.OK

    p_schema = PlayerSchema()
    e_schema = EntrySchema(many=True)
    # TODO: (cf db.PlayerSchema) make it so that p_schema.dump(player automatically generates all the data
    return jsonify(player=p_schema.dump(player),
                   registeredEntries=e_schema.dump(
                       session.scalars(select(Entry).where(Entry.licence_no == licence_no)))), HTTPStatus.OK


@bp.route('/entries', methods=['POST'])
def api_register_entries():
    if 'licenceNo' not in request.json or 'categoryIds' not in request.json:
        return jsonify(error=f"Missing either 'licenceNo' or 'categoryIds' field in json."), HTTPStatus.BAD_REQUEST

    licence_no = request.json['licenceNo']
    category_ids = request.json['categoryIds']

    player = session.scalar(select(Player).filter_by(licence_no=licence_no))
    if player is None:
        return (jsonify(
            error=f"No player with licence number {licence_no} exists in the database. Entry was not registered."),
                HTTPStatus.BAD_REQUEST)
    if not category_ids:
        return jsonify(error="No categories to register entries in were sent."), HTTPStatus.BAD_REQUEST

    existing_category_ids = set(session.scalars(select(Category.category_id)))
    if a := set(category_ids).difference(set(existing_category_ids)):
        return jsonify(
            error=f"No categories with the following categoryIds {a} exist in the database"), HTTPStatus.BAD_REQUEST

    potential_categories = session.scalars(select(Category).where(Category.category_id.in_(category_ids)))

    violations = []
    for category in potential_categories:
        if (category.women_only and player.gender != 'F') or (player.nb_points > category.max_points) or (
                player.nb_points < category.min_points):
            violations.append(category.category_id)
    if violations:
        return jsonify(
            error=f"Tried to register some entries violating either gender or points conditions: {violations}"), HTTPStatus.BAD_REQUEST

    schema = EntrySchema(many=True)
    temp_dicts = [{'categoryId': category_id, 'licenceNo': licence_no} for category_id in category_ids]

    if errors := schema.validate(temp_dicts):
        return jsonify(error=f"Invalid registration data: {errors}"), HTTPStatus.BAD_REQUEST

    query_str = \
        ("INSERT INTO entries (category_id, licence_no, registration_time, color) "
         "VALUES (:categoryId, :licenceNo, NOW(), "
         "(SELECT color FROM categories WHERE category_id = :categoryId)) "
         "ON CONFLICT (category_id, licence_no) DO NOTHING;")
    stmt = text(query_str)

    try:
        session.execute(stmt, temp_dicts)
        session.commit()
        e_schema = EntrySchema(many=True)
        # TODO: (cf db.PlayerSchema) make it so that p_schema.dump(player automatically generates all the data
        return jsonify(entries=e_schema.dump(
            session.scalars(
                select(Entry).where(Entry.licence_no == licence_no).order_by(
                    Entry.category_id)))), HTTPStatus.CREATED
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=f"One or several potential entries violate color constraint. {e}"), HTTPStatus.BAD_REQUEST
