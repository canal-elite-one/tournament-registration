from flask import Blueprint, render_template, current_app

from shared.api.db import is_before_cutoff

public_bp = Blueprint(
    "public",
    __name__,
    url_prefix="/public",
    template_folder="../templates",
)


@public_bp.route("/", methods=["GET"])
def index_page():
    if not is_before_cutoff():
        return render_template("/public_late_index.html")
    return render_template("/public_index.html")


@public_bp.route("/contact", methods=["GET"])
def contact_page():
    return render_template("/public_contact.html")


@public_bp.route("/joueur/<int:licence_no>", methods=["GET"])
def player_page(licence_no):
    return render_template(
        "/public_player.html",
        licence_no=licence_no,
        max_entries_per_day=current_app.config["MAX_ENTRIES_PER_DAY"],
    )


@public_bp.route("/deja_inscrit/<int:licence_no>", methods=["GET"])
def already_registered_page(licence_no):
    return render_template("/public_already_registered.html", licence_no=licence_no)


@public_bp.route("/erreur", methods=["GET"])
def error_page():
    return render_template("/public_unexpected_error.html"), 500


def not_found_page(e):
    return render_template("/public_not_found.html"), 404
