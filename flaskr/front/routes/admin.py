from flask import Blueprint, render_template
from flaskr.db import app_info
from datetime import datetime


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="../templates",
)


@admin_bp.route("/inscrits", methods=["GET"])
def show_all_players():
    return render_template("/show_all_players.html")


@admin_bp.route("/inscrits/<int:licence_no>", methods=["GET"])
def player_page(licence_no):
    if app_info.registration_cutoff is None:
        # TODO: redirect to set categories page
        return None
    if datetime.now() > app_info:
        # TODO: render /admin_player_management_during_tournament
        return None
    return render_template(
        "/admin_player_management_pre_tournament.html",
        licence_no=licence_no,
    )
