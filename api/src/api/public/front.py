import locale
from http import HTTPStatus

from flask import Blueprint, redirect, render_template, current_app, url_for
from sqlalchemy import select

from api.shared.api.db import Session, is_before_cutoff, is_before_start, CategoryInDB

public_bp = Blueprint(
    "public",
    __name__,
    url_prefix="/public",
    template_folder="../templates",
)


@public_bp.route("/", methods=["GET"])
def index_page():
    if not is_before_cutoff():
        return render_template(
            "/public_late_index.html",
            contact_email=current_app.config["USKB_EMAIL"],
        )
    if is_before_start():
        return render_template(
            "/public_early_index.html",
            start_date=current_app.config["TOURNAMENT_REGISTRATION_START"].isoformat(),
        )
    with Session() as session:
        all_categories = session.scalars(
            select(CategoryInDB).order_by(CategoryInDB.start_time),
        ).all()

        saturday_categories = [c for c in all_categories if c.start_time.weekday() == 5]
        sunday_categories = [c for c in all_categories if c.start_time.weekday() == 6]
        locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    return render_template(
        "/public_index.html",
        saturday_categories=saturday_categories,
        sunday_categories=sunday_categories,
        saturday_date=saturday_categories[0].start_time.strftime("%d %B %Y"),
        sunday_date=sunday_categories[0].start_time.strftime("%d %B %Y"),
    )


@public_bp.route("/contact", methods=["GET"])
def contact_page():
    if is_before_start():
        return redirect(url_for("public.index_page"))
    return render_template(
        "/public_contact.html",
        contact_email=current_app.config["USKB_EMAIL"],
        contact_phone=current_app.config["USKB_PHONE"],
        contact_website=current_app.config["USKB_WEBSITE"],
    )


@public_bp.route("/joueur/<licence_no>", methods=["GET"])
def player_page(licence_no):
    if is_before_start():
        return redirect(url_for("public.index_page"))
    return render_template(
        "/public_player.html",
        licence_no=licence_no,
        max_entries_per_day=current_app.config["MAX_ENTRIES_PER_DAY"],
    )


@public_bp.route("/reglement", methods=["GET"])
def ruleset_page():
    if is_before_start():
        return redirect(url_for("public.index_page"))
    return render_template("/public_ruleset.html")


@public_bp.route("/deja_inscrit/<licence_no>", methods=["GET"])
def already_registered_page(licence_no):
    if is_before_start():
        return redirect(url_for("public.index_page"))
    return render_template(
        "/public_already_registered.html",
        licence_no=licence_no,
        contact_email=current_app.config["USKB_EMAIL"],
    )


@public_bp.route("/erreur", methods=["GET"])
def error_page():
    return (
        render_template("/public_unexpected_error.html"),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def not_found_page(e):
    return render_template("/public_not_found.html"), HTTPStatus.NOT_FOUND
