import requests
from const import *
from data import ProgramData
from flask import Blueprint, Response, request
from flask_cors import cross_origin
from flask_server.utils import print_request_info

motor_board_blueprint = Blueprint("motor_board_blueprint", __name__)


@motor_board_blueprint.route("/cars-ready", methods=["POST"])
@cross_origin()
def cars_ready():
    print_request_info(request)

    ProgramData.cars_ready = True

    return Response(status=204)


@motor_board_blueprint.route("/give-start-approval", methods=["POST"])
@cross_origin()
def give_start_approval():
    print_request_info(request)

    if ProgramData.cars_ready:
        ProgramData.approval_given = True
        requests.post(f"http://{MOTOR_BOARD_IP}/give-start-approval")
        return Response(status=204)
    elif DEBUG:
        print("/give-start-approval - Tried to give approval, but cars not ready!")
    return Response(status=400)


@motor_board_blueprint.route("/force-spin-motor", methods=["POST"])
@cross_origin()
def force_spin_motor():
    print_request_info(request)

    ProgramData.cars_ready = False
    ProgramData.approval_given = False

    # Add silent parameter if silent is true (doesn't matter what the value is to the motor board)
    requests.post(f"http://{MOTOR_BOARD_IP}/force-spin-motor", data={"silent": True} if request.json["silent"] == True else None)

    return Response(status=204)


@motor_board_blueprint.route("/run-started", methods=["POST"])
@cross_origin()
def run_started():
    print_request_info(request)

    ProgramData.cars_ready = False
    ProgramData.approval_given = False

    if ProgramData.auto_handle_recording:
        ProgramData.delayed_start_recording(DELAY_FOR_AUTO_START_RECORDING)
    ProgramData.obs_handler.reset_run_times()

    # Tell the timer board about the cool new info we just got
    requests.post(f"http://{TIMER_BOARD_IP}/begin-run")

    return Response(status=204)
