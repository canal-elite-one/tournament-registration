from flask import Blueprint, render_template
from flaskr.api import api_get_player


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
    player_dict = api_get_player(licence_no)[0].json
    return render_template("/show_one_player.html", player_dict=player_dict)
