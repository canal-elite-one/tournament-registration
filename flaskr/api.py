import datetime
from http import HTTPStatus
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from flaskr.db import session, Categories, Players, CategorySchema, PlayerSchema, EntrySchema, Entries
from sqlalchemy import delete, select, text
from sqlalchemy.exc import DBAPIError
import sqlalchemy.dialects.postgresql as psql

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/categories", methods=["POST"])
def api_set_categories():
    """
    Expects a jsonified list of dicts in the "categories" field of the json that can be passed unpacked to the
    category constructor. Don't forget to cast datetime types to some parsable string.
    """

    schema = CategorySchema(many=True)
    try:
        categories = schema.load(request.json['categories'])
    except ValidationError as e:
        return jsonify(
            error=f"Some category data was missing or wrongly formatted. Categories were not set. {e}"), HTTPStatus.BAD_REQUEST
    except KeyError:
        return jsonify(error=f"json was missing 'categories' field. Categories were not set"), HTTPStatus.BAD_REQUEST

    session.execute(delete(Categories))

    try:
        for category in categories:
            session.add(category)
        session.commit()
        return jsonify(categories=
                       schema.dump(session.scalars(
                           select(Categories).order_by(Categories.start_time)).all())), HTTPStatus.CREATED
    except DBAPIError as e:
        session.rollback()
        return jsonify(
            error=f"At least two categories have the same name. Categories were not set. {e}"), HTTPStatus.BAD_REQUEST


@bp.route('/categories', methods=['GET'])
def api_get_categories():
    return jsonify(categories=CategorySchema(many=True).dump(
        session.scalars(select(Categories).order_by(Categories.start_time)))), HTTPStatus.OK


@bp.route('/players', methods=['POST'])
def api_add_player():
    schema = PlayerSchema()
    try:
        player = schema.load(request.json['player'])
    except KeyError:
        return jsonify(error="json was missing 'player' field. Player was not added."), HTTPStatus.BAD_REQUEST
    except ValidationError as e:
        # also triggers if 'bibNo' field is None instead of just not there
        return jsonify(
            error=f"Some player data was missing or wrongly formatted. Player was not added. {e}"), HTTPStatus.BAD_REQUEST
    # TODO: try to do this as a subquery of an insert statement?

    # query_str = \
    #     ("INSERT INTO players (category_id, licence_no, registration_time) "
    #      "VALUES (:categoryID, :licenceNo, :registrationTime, "
    #      "(SELECT min(a) "
    #      "FROM generate_series(1, (SELECT max(bib_no) + 1 FROM players)) AS a "
    #      "WHERE a NOT IN (SELECT bib_no FROM players)))"
    #      "ON CONFLICT (category_id, licence_no) DO NOTHING ;")
    # stmt = text(query_str)

    existing_bib_nos = session.scalars(select(Players.bib_no)).all()
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
def api_get_player_info():
    try:
        licence_no = request.json['licenceNo']
    except KeyError:
        return jsonify(
            error="json was missing 'licenceNo' field. Could not retrieve player info."), HTTPStatus.BAD_REQUEST
    player = session.scalar(select(Players).where(Players.licence_no == licence_no))
    if player is None:
        return jsonify(player=None, registeredCategories=[]), HTTPStatus.OK
    p_schema = PlayerSchema()
    e_schema = EntrySchema(many=True)
    # TODO: (cf db.PlayerSchema) make it so that p_schema.dump(player automatically generates all the data
    return jsonify(player=p_schema.dump(player),
                   registeredCategories=e_schema.dump(
                       session.scalars(select(Entries).where(Entries.licence_no == licence_no)))), HTTPStatus.OK


@bp.route('/register', methods=['POST'])
def api_register_entries():
    try:
        licence_no = request.json['licenceNo']
        category_ids = request.json['categoryIDs']
    except KeyError as e:
        return jsonify(
            error=f"Missing either 'licenceNo' or 'categoryIDs' field in json. {e}"), HTTPStatus.BAD_REQUEST

    if session.scalar(select(Players).where(Players.licence_no == licence_no)) is None:
        return (jsonify(
            error=f"No player with licence number {licence_no} exists in the database. Entry was not registered."),
                HTTPStatus.BAD_REQUEST)
    if not category_ids:
        return jsonify(error="No categories to register entries in were sent."), HTTPStatus.BAD_REQUEST
    existing_categories = set(session.scalars(select(Categories.category_id)))
    if a := set(category_ids).difference(set(existing_categories)):
        return jsonify(
            error=f"No categories with the following categoryIDs {a} exist in the database"), HTTPStatus.BAD_REQUEST

    schema = EntrySchema(many=True)
    temp_dicts = [{'categoryID': category_id, 'licenceNo': licence_no,
                   'registrationTime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
                  for category_id in category_ids]
    # TODO: change validate to load and temp_dict to .dump() in psql.insert().values(...) ?
    if errors := schema.validate(temp_dicts):
        return jsonify(error=f"Invalid registration data: {errors}"), HTTPStatus.BAD_REQUEST

    query_str = \
        ("INSERT INTO entries (category_id, licence_no, registration_time, color) "
         "VALUES (:categoryID, :licenceNo, :registrationTime, "
                                    "(SELECT color FROM categories WHERE category_id = :categoryID))"
         "ON CONFLICT (category_id, licence_no) DO NOTHING ;")
    stmt = text(query_str)

    # stmt = psql.insert(Entries).values([entry.__dict__ for entry in entries])
    # stmt = stmt.on_conflict_do_nothing(index_elements=['category_id', 'licence_no'])
    try:
        session.execute(stmt, temp_dicts)
        session.commit()
        # Est-ce que c'est ça qu'il faut faire comme réponse ? comment éviter les problèmes de commit
        return jsonify(entries=schema.dump(
            session.scalars(select(Entries).where(Entries.licence_no == licence_no).order_by(Entries.category_id)))), HTTPStatus.OK
    except DBAPIError as e:
        session.rollback()
        return jsonify(error=f"One or several potential entries violate color constraint. {e}"), HTTPStatus.BAD_REQUEST
