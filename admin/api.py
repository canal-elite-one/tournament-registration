from collections import Counter
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
    ContactInfoSchema,
    EntrySchema,
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
e_schema = EntrySchema()

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
                error_message=ae.RegistrationMessages.STARTED,
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


@api_bp.route("/players/<licence_no>", methods=["GET"])
def api_admin_get_player(licence_no):
    origin = api_admin_get_player.__name__
    with Session() as session:
        if (player := session.get(Player, licence_no)) is not None:
            p_schema.reset(include_entries=True, include_payment_status=True)
            return jsonify(p_schema.dump(player)), HTTPStatus.OK

    if request.args.get("db_only", False, loads) is True:
        raise ae.PlayerNotFoundError(
            origin=f"{origin}_db_only",
            licence_no=licence_no,
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
        raise ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )

    player.total_actual_paid = 0

    include_entries_info = not is_before_cutoff()
    p_schema.reset(
        include_entries=include_entries_info,
        include_payment_status=include_entries_info,
    )
    return jsonify(p_schema.dump(player)), HTTPStatus.OK


@api_bp.route("/players/<licence_no>", methods=["POST"])
def api_admin_add_player(licence_no):
    origin = api_admin_add_player.__name__
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

    p_schema.reset()

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


@api_bp.route("/entries/<licence_no>", methods=["POST"])
def api_admin_register_entries(licence_no):
    """
    expects a json payload of the form: {"totalActualPaid": XX, "entries": [{...}, ...]}
    with entries of the form:
    {"categoryId": "X", "markedAsPresent": true/false/null, "markedAsPaid": true/false}
    The total_actual_paid field is not required before cutoff.

    The endpoint considers the payload to represent all the entries for the player
    after the request. In particular, it deletes all entries for the player that are not
    in the payload, and updates the other entries with the information in the payload.
    The endpoint also updates the totalActualPaid field of the player with the value
    in the payload.
    The endpoint preserves the registration_time of the entries that are not deleted.

    Note that the endpoint consciously does not enforce the following constraints,
    allowing the admin to override them if need be:
    - the player must not register to more than MAX_ENTRIES_PER_DAY categories per day
    - if female, the player must register to the women_only category of the day if she
        registers to any category of the day

    Enforced format/logic constraints:
    - totalActualPaid field must be present and not null after cutoff
    - totalActualPaid field must be zero or not present before cutoff
    - the licence_no must correspond to an existing player in the database
    - the entries must be correctly formatted
    - the category_ids must correspond to existing categories in the database
    - the player must be able to register to all categories indicated w.r.t
        gender/points constraints
    - the request must not try to register to more than one category of the same color
    - the request must not try to mark entries as paid or present before cutoff
    - the request must not try to mark entries as paid without marking them as present
    - the request must not try to mark entries as present for categories that have
        already max_players present players
    - the totalActualPaid field must not be higher than the total fees for the
        categories the player is marked as present for (after the changes)
    """
    origin = api_admin_register_entries.__name__
    data = request.json

    total_actual_paid = data.get("totalActualPaid", None)
    if total_actual_paid is None:
        # checks that the total_actual_paid field is present and not null,
        # except if the registration period has not already ended, in which case
        # the field is not required
        if not is_before_cutoff():
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.PAYMENT_FORMAT_MESSAGE,
                payload={"totalActualPaid": "Field is missing or null"},
            )
        total_actual_paid = 0
    # if the registration period has not already ended,
    # the total_actual_paid field must be zero
    elif is_before_cutoff() and total_actual_paid > 0:
        raise ae.RegistrationCutoffError(
            origin=origin,
            error_message=ae.RegistrationMessages.NOT_ENDED_ACTUAL_MAKE_PAYMENT,
            payload={"totalActualPaid": total_actual_paid},
        )

    with Session() as session:
        player = session.get(Player, licence_no)
        # checks that the player exists in the database (not just in FFTT)
        if player is None:
            raise ae.PlayerNotFoundError(
                origin=origin,
                licence_no=licence_no,
            )

        e_schema.reset(many=True)

        # checks that entries data is correctly formatted
        try:
            new_entries = e_schema.load(data)
        except ValidationError as e:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.REGISTRATION_FORMAT_MESSAGE,
                payload=e.messages,
            )

        new_entry_category_ids = {entry.category_id for entry in new_entries}
        old_entries = list(player.entries)
        old_entry_category_ids = {entry.category_id for entry in old_entries}

        # checks that all category ids are valid
        nonexisting_category_ids = new_entry_category_ids.difference(
            session.scalars(select(Category.category_id)),
        )
        if nonexisting_category_ids:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
                payload={
                    "categoryIds": sorted(nonexisting_category_ids),
                },
            )

        # We use list comprehension here instead of session.scalars(
        # select(Category).where(Category.category_id.in_(new_entry_category_ids))
        # ).all() to preserve the order.
        potential_categories = [
            session.get(Category, entry.category_id) for entry in new_entries
        ]
        # checks that the player can register to all categories indicated
        # w.r.t gender/points constraints
        gender_points_violations = [
            category.category_id
            for category in potential_categories
            if not player.respects_gender_points_constraints(category)
        ]
        if gender_points_violations:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.GENDER_POINTS_VIOLATION_MESSAGE,
                payload={
                    "categoryIds": sorted(gender_points_violations),
                },
            )

        # checks that the player does not try to register to
        # more than one category of the same color
        max_entries_per_color = max(
            Counter(
                category.color
                for category in potential_categories
                if category.color is not None
            ).values()
            or [0],
        )
        if max_entries_per_color > 1:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.COLOR_VIOLATION_MESSAGE,
            )

        # checks that the request does not try to mark entries as paid or present
        # before the registration period has ended (marking as absent is possible)
        if is_before_cutoff():
            present_category_ids = [
                entry.category_id
                for entry in new_entries
                if entry.marked_as_present is True
            ]
            paid_category_ids = [
                entry.category_id
                for entry in new_entries
                if entry.marked_as_paid is True
            ]
            if present_category_ids or paid_category_ids:
                raise ae.RegistrationCutoffError(
                    origin=origin,
                    error_message=ae.RegistrationMessages.NOT_ENDED_MARK_PRESENT_MAKE_PAYMENT,
                    payload={
                        "categoryIdsPresent": present_category_ids,
                        "categoryIdsPaid": paid_category_ids,
                    },
                )

        # checks that the request does not try to mark entries as paid
        # without marking them as present
        nonpresent_payment_entries = [
            entry.category_id
            for entry in new_entries
            if (
                (entry.marked_as_present is None or entry.marked_as_present is False)
                and entry.marked_as_paid is True
            )
        ]
        if nonpresent_payment_entries:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.PAYMENT_PRESENT_VIOLATION_MESSAGE,
                payload={
                    "categoryIds": sorted(nonpresent_payment_entries),
                },
            )

        # checks that the request does not try to mark entries as present
        # for categories that have already max_players present players
        # (and that were not previously marked as present).
        # Note that here new entries are not yet associated with the session,
        # which implies that the session.get(Entry, ...) call only returns old entries.
        # However, this also means that we have to use session.get(Category, ...)
        # instead of simply entry.category.
        category_ids_with_too_many_present = [
            entry.category_id
            for entry in new_entries
            if (
                entry.marked_as_present is True
                and (
                    entry.category_id not in old_entry_category_ids
                    or session.get(
                        Entry,
                        (entry.category_id, licence_no),
                    ).marked_as_present
                    is not True
                )
                and len(session.get(Category, entry.category_id).present_entries())
                >= session.get(Category, entry.category_id).max_players
            )
        ]
        if category_ids_with_too_many_present:
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.CATEGORY_FULL_PRESENT_MESSAGE,
                payload={
                    "categoryIds": sorted(category_ids_with_too_many_present),
                },
            )

        # we need to update the session objects here to be able to compute the
        # fees_total_present for the last constraint check.
        # we actually need to use the relationship syntax instead of the
        # session.add/delete syntax because the latter does not update the
        # relationships before committing, and we need updated relationships
        # for the computation of fees_total_present
        for i, entry in list(enumerate(old_entries))[::-1]:
            if entry.category_id not in new_entry_category_ids:
                del player.entries[i]

        for entry, category in zip(new_entries, potential_categories):
            entry.licence_no = licence_no
            if entry.category_id not in old_entry_category_ids:
                entry.registration_time = datetime.now()
                player.entries.append(entry)
                category.entries.append(entry)
            else:
                session.merge(entry)

        player.total_actual_paid = total_actual_paid

        # checks that the total_actual_paid field is not higher than the total fees
        # for the categories the player is marked as present for.
        # If it is, the changes just above are rolled back.
        if (total_present := player.fees_total_present()) < total_actual_paid:
            # need to store the value of fees_total_present before rollback
            # to be able to return it in the error message
            session.rollback()
            raise ae.InvalidDataError(
                origin=origin,
                error_message=ae.ACTUAL_PAID_TOO_HIGH_MESSAGE,
                payload={
                    "totalActualPaid": total_actual_paid,
                    "totalPresent": total_present,
                },
            )

        try:
            session.commit()
        except DBAPIError as e:
            session.rollback()
            raise ae.UnexpectedDBError(
                origin=origin,
                exception=e,
            )

        p_schema.reset(include_entries=True, include_payment_status=True)
        return jsonify(p_schema.dump(player)), HTTPStatus.CREATED


@api_bp.route("/players/<licence_no>", methods=["DELETE"])
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


@api_bp.route("/bibs/<licence_no>", methods=["PUT"])
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
    c_schema.reset(many=True, include_players=True, present_only=present_only)

    with Session() as session:
        categories = session.scalars(
            select(Category).order_by(Category.start_time),
        ).all()
        return jsonify(c_schema.dump(categories)), HTTPStatus.OK


@api_bp.route("/players/all", methods=["GET"])
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

    p_schema.reset(
        many=True,
        simple_entries=True,
        include_payment_status=not is_before_cutoff(),
    )

    with Session() as session:
        return (
            jsonify(players=p_schema.dump(session.scalars(query).all())),
            HTTPStatus.OK,
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
                players.append(
                    [
                        entry.player
                        for entry in sorted(
                            category.entries,
                            key=lambda e: e.registration_time,
                        )
                        if entry.marked_as_present is not False
                    ][: category.max_players],
                )
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
                .where(Entry.category_id.in_(saturday_category_ids))
                .order_by(Player.bib_no),
            ).all()
            sunday_players = session.scalars(
                select(Player)
                .distinct()
                .join(Entry)
                .where(Entry.category_id.in_(sunday_category_ids))
                .order_by(Player.bib_no),
            ).all()
            all_players = session.scalars(
                select(Player).distinct().order_by(Player.bib_no),
            ).all()

            players = [saturday_players, sunday_players, all_players]
            filenames = [
                "competiteurs_samedi.csv",
                "competiteurs_dimanche.csv",
                "competieurs.csv",
            ]
            zip_name = "competiteurs_samedi_dimanche"

        return create_zip_file(filenames, players, zip_name)


def create_zip_file(filenames: list[str], players: list[list], zip_name: str):
    zip_file = BytesIO()

    def player_str(player_object):
        return (
            f"{player_object.bib_no},{player_object.licence_no},"
            f"{player_object.last_name},{player_object.first_name},"
            f"{player_object.nb_points},{player_object.club}\n"
        )

    with ZipFile(zip_file, "w") as zip_zip:
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
