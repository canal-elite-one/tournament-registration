from datetime import datetime
from io import BytesIO
from json import loads
from http import HTTPStatus
from zipfile import ZipFile

from flask import Blueprint, jsonify, request, Response
from marshmallow import ValidationError
from sqlalchemy import select, delete, distinct, func, update, text
from sqlalchemy.exc import DBAPIError

from shared.api.fftt_api import get_player_fftt
from shared.api.marshmallow_schemas import (
    CategorySchema,
    PlayerSchema,
    MakePaymentSchema,
    CategoryIdsSchema,
)
from shared.api.db import (
    Category,
    Player,
    Entry,
    Session,
    is_before_cutoff,
)
import shared.api.api_errors as ae
from shared.api.custom_decorators import after_cutoff

c_schema = CategorySchema()
p_schema = PlayerSchema()

api_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")


@api_bp.route("/categories", methods=["POST"])
def api_admin_set_categories():
    """
    Expects a jsonified list of dicts in the "categories" field of the json that can be
    passed unpacked to the category constructor. Don't forget to cast datetime types
    to some parsable string.
    """
    origin = api_admin_set_categories.__name__

    c_schema.reset(many=True)
    try:
        categories = c_schema.load(request.json)
    except ValidationError as e:
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.CATEGORY_FORMAT_MESSAGE,
            payload=e.messages,
        )

    with Session() as session:
        try:
            session.execute(delete(Category))
        except DBAPIError:
            session.rollback()
            raise ae.RegistrationCutoffError(
                origin=origin,
                error_message=ae.REGISTRATION_MESSAGES["started"],
            )

        try:
            for category in categories:
                session.add(category)
            session.commit()

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
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )


@api_bp.route("/categories", methods=["GET"])
def api_admin_get_categories():
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


@api_bp.route("/players/<int:licence_no>", methods=["GET"])
def api_admin_get_player(licence_no):
    origin = api_admin_get_player.__name__
    with Session() as session:
        if (player := session.get(Player, licence_no)) is not None:
            p_schema.reset()
            p_schema.context["include_entries"] = True
            p_schema.context["include_payment_status"] = True
            return jsonify(p_schema.dump(player)), HTTPStatus.OK

    if request.args.get("db_only", False, loads) is True:
        raise ae.PlayerNotFoundError(
            origin=origin + "_db_only",
            licence_no=licence_no,
        )

    try:
        player_dict = get_player_fftt(licence_no)
    except ae.FFTTAPIError:
        raise ae.UnexpectedFFTTError(
            origin=origin,
            payload=None,
        )

    if player_dict is None:
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    return jsonify(player_dict), HTTPStatus.OK


@api_bp.route("/players", methods=["POST"])
def api_admin_add_player():
    origin = api_admin_add_player.__name__
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


@api_bp.route("/entries/<int:licence_no>", methods=["POST"])
def api_admin_register_entries(licence_no):
    origin = api_admin_register_entries.__name__

    v_schema = CategoryIdsSchema()
    if error := v_schema.validate(request.json):
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.REGISTRATION_FORMAT_MESSAGE,
            payload=error,
        )

    category_ids = request.json["categoryIds"]

    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        if not category_ids:
            p_schema.reset()
            p_schema.context["include_entries"] = True
            p_schema.context["include_payment_status"] = True
            return jsonify(p_schema.dump(player)), HTTPStatus.CREATED

        if nonexisting_category_ids := set(category_ids).difference(
            session.scalars(select(Category.category_id)),
        ):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
                payload={
                    "categoryIds": sorted(nonexisting_category_ids),
                },
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
                payload={
                    "categoryIds": sorted(violations),
                },
            )

        temp_dicts = [
            {
                "categoryId": category_id,
                "licenceNo": licence_no,
                "registrationTime": datetime.now(),
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
            p_schema.reset()
            p_schema.context["include_entries"] = True
            p_schema.context["include_payment_status"] = True
            return jsonify(p_schema.dump(player)), HTTPStatus.CREATED
        except DBAPIError:
            session.rollback()
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.COLOR_VIOLATION_MESSAGE,
            )


@api_bp.route("/pay/<int:licence_no>", methods=["PUT"])
@after_cutoff
def api_admin_make_payment(licence_no):
    origin = api_admin_make_payment.__name__

    v_schema = MakePaymentSchema()
    if error := v_schema.validate(request.json):
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.PAYMENT_FORMAT_MESSAGE,
            payload=error,
        )

    with Session() as session:
        if (player := session.get(Player, licence_no)) is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        ids_to_pay = set(request.json["categoryIds"])

        if invalid_category_ids := ids_to_pay.difference(
            entry.category_id for entry in player.present_entries()
        ):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["payment"],
                payload={
                    "categoryIds": sorted(invalid_category_ids),
                },
            )

        for entry in player.present_entries():
            if entry.category_id in ids_to_pay:
                entry.marked_as_paid = True

        total_actual_paid = request.json["totalActualPaid"]

        if player.fees_total_present() < total_actual_paid:
            session.rollback()
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.ACTUAL_PAID_TOO_HIGH_MESSAGE,
                payload={
                    "totalActualPaid": total_actual_paid,
                    "totalPresent": player.fees_total_present(),
                },
            )

        player.total_actual_paid = total_actual_paid

        try:
            session.commit()
        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )

        p_schema.reset()
        p_schema.context["include_entries"] = True
        p_schema.context["include_payment_status"] = True
        return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/entries/<int:licence_no>", methods=["DELETE"])
def api_admin_delete_entries(licence_no):
    origin = api_admin_delete_entries.__name__
    v_schema = CategoryIdsSchema()
    if error := v_schema.validate(request.json):
        raise ae.InvalidDataError(
            origin=origin,
            error_message=ae.DELETE_ENTRIES_FORMAT_MESSAGE,
            payload=error,
        )

    category_ids = request.json["categoryIds"]

    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        if unregistered_category_ids := set(category_ids).difference(
            entry.category_id for entry in player.entries
        ):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["deletion"],
                payload={
                    "categoryIds": sorted(unregistered_category_ids),
                },
            )

        try:
            session.execute(
                delete(Entry).where(
                    Entry.licence_no == licence_no,
                    Entry.category_id.in_(category_ids),
                ),
            )
            session.commit()
            p_schema.reset()
            p_schema.context["include_entries"] = True
            p_schema.context["include_payment_status"] = True
            return jsonify(p_schema.dump(player)), HTTPStatus.OK

        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )


@api_bp.route("/players/<int:licence_no>", methods=["DELETE"])
def api_admin_delete_player(licence_no):
    origin = api_admin_delete_player.__name__
    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        try:
            session.delete(player)
            session.commit()
            return Response(status=HTTPStatus.NO_CONTENT)
        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )


@api_bp.route("/present/<int:licence_no>", methods=["PUT"])
def api_admin_mark_present(licence_no):
    """
    This is the only way to unpay an entry:
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
    origin = api_admin_mark_present.__name__
    with Session() as session:
        player = session.get(Player, licence_no)
        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        all_ids_to_update = request.json.get("categoryIdsPresence", {})

        if unregistered_nonexisting_categories := set(
            all_ids_to_update.keys(),
        ).difference(entry.category_id for entry in player.entries):
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["present"],
                payload={
                    "categoryIds": sorted(unregistered_nonexisting_categories),
                },
            )

        too_many_present_category_ids = []
        for category_id, presence in all_ids_to_update.items():
            if presence is True:
                category = session.get(Category, category_id)
                if (
                    len(list(category.present_entries())) > category.max_players
                    and session.get(Entry, (category_id, licence_no)) is None
                ):
                    too_many_present_category_ids.append(category_id)

                if too_many_present_category_ids:
                    raise ae.InvalidDataError(
                        origin=origin,
                        error_message=ae.CATEGORY_FULL_PRESENT_MESSAGE,
                        payload={
                            "categoryIds": sorted(too_many_present_category_ids),
                        },
                    )

        for category_id, presence in all_ids_to_update.items():
            entry = session.get(Entry, (category_id, licence_no))
            entry.marked_as_present = presence
            if presence and is_before_cutoff():
                raise ae.RegistrationCutoffError(
                    origin=origin,
                    error_message=ae.REGISTRATION_MESSAGES["not_ended_mark_present"],
                )
            if presence is None or presence is False:
                entry.marked_as_paid = False

        player.total_actual_paid = min(
            player.fees_total_present(),
            player.total_actual_paid,
        )

        try:
            session.commit()
        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )

        p_schema.reset()
        p_schema.context["include_entries"] = True
        p_schema.context["include_payment_status"] = True
        return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/bibs", methods=["POST"])
@after_cutoff
def api_admin_assign_all_bibs():
    origin = api_admin_assign_all_bibs.__name__
    with Session() as session:
        player_with_bibs = session.scalars(
            select(Player.licence_no).where(Player.bib_no.isnot(None)),
        ).all()
        if player_with_bibs:
            raise ae.BibConflictError(
                origin=origin,
                error_message=ae.SOME_BIBS_ALREADY_ASSIGNED_MESSAGE,
                payload={"licenceNos": sorted(player_with_bibs)},
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
        try:
            session.execute(update(Player), assigned_bib_nos)
            session.commit()
        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )
    return jsonify(assignedBibs=assigned_bib_nos), HTTPStatus.OK


@api_bp.route("/bibs/<int:licence_no>", methods=["PUT"])
@after_cutoff
def api_admin_assign_one_bib(licence_no):
    origin = api_admin_assign_one_bib.__name__
    with Session() as session:
        player = session.get(Player, licence_no)

        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        if player.bib_no is not None:
            raise ae.BibConflictError(
                origin=origin,
                error_message=ae.THIS_BIB_ALREADY_ASSIGNED_MESSAGE,
                payload={"licenceNo": licence_no, "bibNo": player.bib_no},
            )

        if session.scalars(select(distinct(Player.bib_no))).all() == [None]:
            raise ae.BibConflictError(
                origin=origin,
                error_message=ae.NO_BIBS_ASSIGNED_MESSAGE,
            )

        session.execute(
            text(
                "UPDATE players SET "
                "bib_no = (SELECT MAX(bib_no) + 1 FROM players) "
                "WHERE licence_no = :licence_no;",
            ),
            {"licence_no": player.licence_no},
        )
        try:
            session.commit()
        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )
        p_schema.reset()
        return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/bibs", methods=["DELETE"])
@after_cutoff
def api_admin_reset_bibs():
    origin = api_admin_reset_bibs.__name__
    confirmation = request.json.get("confirmation", None)
    if confirmation != ae.RESET_BIBS_CONFIRMATION:
        raise ae.ConfirmationError(
            origin=origin,
            error_message=ae.RESET_BIBS_CONFIRMATION_MESSAGE,
        )
    with Session() as session:
        try:
            session.execute(update(Player).values(bib_no=None))
            session.commit()
        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )

    return jsonify(success="success"), HTTPStatus.NO_CONTENT


@api_bp.route("/by_category", methods=["GET"])
def api_admin_get_players_by_category():
    present_only = request.args.get("present_only", False, loads) is True
    c_schema.reset(many=True)
    c_schema.context["include_players"] = True
    c_schema.context["present_only"] = present_only

    with Session() as session:
        categories = session.scalars(
            select(Category).order_by(Category.start_time),
        ).all()
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

    p_schema.reset(many=True)
    p_schema.context["simple_entries"] = True
    p_schema.context["include_payment_status"] = True

    with Session() as session:
        return (
            jsonify(players=p_schema.dump(session.scalars(query).all())),
            HTTPStatus.OK,
        )


def create_zip_file(filenames: list[str], players: list[list], zip_name: str):
    zip_file = BytesIO()

    def player_str(player_object):
        return (
            f"{player_object.bib_no},{player_object.licence_no},"
            f"{player_object.last_name},{player_object.first_name},"
            f"{player_object.nb_points},{player_object.club}\n"
        )

    with ZipFile(zip_file, "a") as zip_zip:
        for filename, player_list in zip(filenames, players):
            content = ["N° dossard, N° licence, Nom, Prénom, Points, Club\n"]
            content.extend(player_str(player) for player in player_list)
            zip_zip.writestr(
                filename,
                "".join(content),
            )

    zip_file.seek(0)
    return Response(
        zip_file.getvalue(),
        mimetype="application/zip",
        headers={
            "Content-Disposition": f"attachment;filename={zip_name}.zip",
        },
    )


@api_bp.route("/csv", methods=["GET"])
def api_admin_get_csv_zip():
    by_category = request.args.get("by_category", False, loads) is True

    with Session() as session:
        if by_category:
            players = []
            filenames = []
            for category in session.scalars(
                select(Category).order_by(Category.start_time),
            ).all():
                players.append([entry.player for entry in category.entries])
                filenames.append(f"competiteurs_tableau_{category.category_id}.csv")
            zip_name = "competiteurs_par_tableaux"
        else:
            categories = session.scalars(select(Category)).all()
            saturday_category_ids = [
                category.category_id
                for category in categories
                if category.start_time.weekday() == 5
            ]
            sunday_category_ids = [
                category.category_id
                for category in categories
                if category.start_time.weekday() == 6
            ]
            saturday_players = session.scalars(
                select(Player)
                .distinct()
                .join(Entry)
                .where(Entry.category_id.in_(saturday_category_ids)),
            ).all()
            sunday_players = session.scalars(
                select(Player)
                .distinct()
                .join(Entry)
                .where(Entry.category_id.in_(sunday_category_ids)),
            ).all()

            players = [saturday_players, sunday_players]
            filenames = ["competiteurs_samedi.csv", "competiteurs_dimanche.csv"]
            zip_name = "competiteurs_samedi_dimanche"

        return create_zip_file(filenames, players, zip_name)
