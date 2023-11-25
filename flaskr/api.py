from flask import Blueprint, request, Response, jsonify
from flaskr.db import session, Categories
from sqlalchemy import delete, select
import logging
from sqlalchemy.exc import DBAPIError

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/categories", methods=["POST"])
def api_set_categories():
    """
    For post requests, expects a jsonified list of dicts that can be passed unpacked to the category constructor.
    Don't forget to cast datetime types to some parsable string.
    """
    session.execute(delete(Categories))
    for cat_dict in request.json:
        session.add(Categories(**cat_dict))

    try:
        session.commit()
        return Response(status=201)
    except DBAPIError as e:
        return Response('Some category data was missing or incorrect. Categories were not set.' + e.statement, status=400)


@bp.route('/categories', methods=['GET'])
def api_get_categories():
    cats = session.scalars(select(Categories).order_by(Categories.start_time)).all()
    return [cat.to_dict() for cat in cats]
