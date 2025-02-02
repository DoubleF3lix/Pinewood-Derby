from flask import Blueprint, Response, request
from flask_cors import cross_origin

from const import *
from data import ProgramData
from flask_server.utils import post_request, print_request_info

timer_board_blueprint = Blueprint("timer_board_blueprint", __name__)


# Data is taken in the form of "<laneID>&<finishedTime>&<position>&<wasFail>"
@timer_board_blueprint.route("/lane-end-triggered", methods=["POST"])
@cross_origin()
def lane_end_triggered():
    print_request_info(request)

    # Do nothing further if we're ignoring data
    if ProgramData.ignore_incoming_data_from_timer:
        return Response(204)

    ProgramData.should_refresh_table = True

    data_in: str = str(request.data, "utf-8")
    data_in = data_in.split("&")

    lane_ID: int = int(data_in[0])

    # If the run count is even, swap the lane IDs so that left is reported for right and vice versa due to the cars swapping lanes every other run
    # Check that, it's supposed to be odd, since it's reversed for some reason...?
    if ProgramData.run_count % 2 == 1:
        lane_ID = 3 - lane_ID

    if lane_ID == 1:
        ProgramData.left_lane_submitted = True
    elif lane_ID == 2:
        ProgramData.right_lane_submitted = True
    
    if ProgramData.left_lane_submitted and ProgramData.right_lane_submitted:
        ProgramData.run_count += 1
        ProgramData.left_lane_submitted = False
        ProgramData.right_lane_submitted = False
        
        if ProgramData.auto_handle_recording:
            ProgramData.obs_handler.stop_recording()

    # Convert milliseconds to a float with centisecond precision, chopping off the last digit (8176 => 817 => 8.17)
    finish_time: int = round(int(data_in[1]) // 10 / 100, 2)
    was_fail: bool = bool(int(data_in[3]))

    # Fail time is set to 10 seconds on the board, override by uncommenting below
    # if was_fail:
    #     finish_time = 10

    run_report = [[finish_time, None], [None, finish_time]][lane_ID - 1]
    ProgramData.active_tourney.append_run(*run_report)

    ProgramData.obs_handler.set_run_time(
        lane_ID, "No Finish" if was_fail else "{:.2f}".format(finish_time)
    )
    ProgramData.obs_handler.set_race_time(lane_ID, "{:.2f}".format(ProgramData.active_tourney.get_race_time_from_runs(lane_ID - 1)))

    return Response(status=204)


@timer_board_blueprint.route("/mark-finish", methods=["POST"])
@cross_origin()
def mark_finish():
    print_request_info(request)

    lane: int = request.json["lane"]
    if lane not in {1, 2}:
        return Response(status=400)

    post_request(f"http://{TIMER_BOARD_IP}/mark-finish", data={"lane": lane})

    return Response(status=204)


@timer_board_blueprint.route("/mark-fail", methods=["POST"])
@cross_origin()
def mark_fail():
    print_request_info(request)

    lane: int = request.json["lane"]
    if lane not in {1, 2}:
        return Response(status=400)

    post_request(f"http://{TIMER_BOARD_IP}/mark-fail", data={"lane": lane})

    return Response(status=204)


@timer_board_blueprint.route("/set-lane-position", methods=["POST"])
@cross_origin()
def set_lane_position():
    print_request_info(request)

    lane: int = request.json["lane"]
    if lane not in {1, 2}:
        return Response(status=400)

    value: int = request.json["value"]

    post_request(f"http://{TIMER_BOARD_IP}/set-position", data={"lane": lane, "value": value})

    return Response(status=204)


@timer_board_blueprint.route("/set-lane-run-time", methods=["POST"])
@cross_origin()
def set_lane_run_timer():
    print_request_info(request)

    lane: str = request.json["lane"]
    if lane not in {1, 2}:
        return Response(status=400)

    value: int = request.json["value"]

    post_request(f"http://{TIMER_BOARD_IP}/set-run-time", data={"lane": lane, "value": value})

    return Response(status=204)


@timer_board_blueprint.route("/edit-show-time-on-finish", methods=["POST"])
@cross_origin()
def edit_show_time_on_finish():
    print_request_info(request)

    value: bool = request.json["value"]

    post_request(f"http://{TIMER_BOARD_IP}/edit-show-time-on-finish", data={"lane": 1, "value": int(value)})
    post_request(f"http://{TIMER_BOARD_IP}/edit-show-time-on-finish", data={"lane": 2, "value": int(value)})

    return Response(status=204)



@timer_board_blueprint.route("/edit-lane-position-visibility", methods=["POST"])
@cross_origin()
def edit_lane_position_visibility():
    print_request_info(request)

    lane: str = request.json["lane"]
    if lane not in {1, 2}:
        return Response(status=400)

    visibility: bool = request.json["visibility"]
    endpoint = "show-position" if visibility else "hide-position"

    post_request(f"http://{TIMER_BOARD_IP}/{endpoint}", data={"lane": lane})

    return Response(status=204)


@timer_board_blueprint.route("/edit-lane-run-time-visibility", methods=["POST"])
@cross_origin()
def edit_lane_run_time_visibility():
    print_request_info(request)

    lane: str = request.json["lane"]
    if lane not in {1, 2}:
        return Response(status=400)

    visibility: bool = request.json["visibility"]
    endpoint = "show-run-time" if visibility else "hide-run-time"

    post_request(f"http://{TIMER_BOARD_IP}/{endpoint}", data={"lane": lane})

    return Response(status=204)
