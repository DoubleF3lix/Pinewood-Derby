from flask import Blueprint, Response, jsonify
from flask_cors import cross_origin

from data import ProgramData

continuous_blueprint = Blueprint("continuous_blueprint", __name__)


@continuous_blueprint.route("/check-connectivity", methods=["GET"])
@cross_origin()
def check_connectivity():
    return Response(status=204)


@continuous_blueprint.route("/check-emcee-alert", methods=["GET"])
@cross_origin()
def check_emcee_alert():
    return {"message": ProgramData.alert_emcee}, 200


@continuous_blueprint.route("/clear-emcee-alert", methods=["POST"])
@cross_origin()
def clear_emcee_alert():
    ProgramData.alert_emcee = ""
    return Response(status=204)


@continuous_blueprint.route("/check-controller-alert", methods=["GET"])
@cross_origin()
def check_controller_alert():
    return jsonify(ProgramData.alert_controller), 200


@continuous_blueprint.route("/clear-controller-alert", methods=["POST"])
@cross_origin()
def clear_controller_alert():
    ProgramData.alert_controller = False
    return Response(status=204)


@continuous_blueprint.route("/check-controller-alert-from-tourney", methods=["GET"])
@cross_origin()
def check_controller_alert_from_tourney():
    return ProgramData.alert_controller_from_tourney, 200


@continuous_blueprint.route("/clear-controller-alert-from-tourney", methods=["POST"])
@cross_origin()
def clear_controller_alert_from_tourney():
    del ProgramData.alert_controller_from_tourney[0]
    return Response(status=204)


@continuous_blueprint.route("/check-should-refresh-table", methods=["GET"])
@cross_origin()
def check_should_refresh_table():
    return jsonify(ProgramData.should_refresh_table), 200


@continuous_blueprint.route("/clear-should-refresh-table", methods=["POST"])
@cross_origin()
def clear_should_refresh_table():
    ProgramData.should_refresh_table = False
    return Response(status=204)


@continuous_blueprint.route("/check-cars-ready", methods=["GET"])
@cross_origin()
def check_cars_ready():
    return jsonify(ProgramData.cars_ready), 200


@continuous_blueprint.route("/get-race-info", methods=["GET"])
@cross_origin()
def get_racers():
    return {
        "now": ProgramData.now_racing, 
        "next": ProgramData.up_next,
        "races_left_in_round": ProgramData.races_left_in_round,
        "players_left": ProgramData.players_left,
    }, 200
