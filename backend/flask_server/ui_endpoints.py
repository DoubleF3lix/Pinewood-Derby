import requests
import tinydb
from const import *
from data import ProgramData
from flask import Blueprint, Response, request
from flask_cors import cross_origin
from flask_server.utils import pad_decimals, print_request_info
from misc.obs_handler import obs_scene

ui_blueprint = Blueprint("ui_blueprint", __name__)


@ui_blueprint.route("/alert-controller", methods=["POST"])
@cross_origin()
def alert_controller():
    print_request_info(request)

    ProgramData.alert_controller = True

    return Response(status=204)


@ui_blueprint.route("/alert-controller-from-tourney", methods=["POST"])
@cross_origin()
def alert_controller_from_tourney():
    print_request_info(request)

    ProgramData.alert_controller_from_tourney.append(request.json["message"])

    return Response(status=204)


@ui_blueprint.route("/alert-emcee", methods=["POST"])
@cross_origin()
def alert_emcee():
    print_request_info(request)

    ProgramData.alert_emcee = request.json["message"]

    return Response(status=204)


@ui_blueprint.route("/get-race-data", methods=["GET"])
@cross_origin()
def get_race_data():
    print_request_info(request)

    return {"runs": ProgramData.active_tourney.current_race_data["runs"]}, 200


@ui_blueprint.route("/update-race-data", methods=["POST"])
@cross_origin()
def update_race_data():
    print_request_info(request)

    # request.json is the direct output of the table, so we can just store it directly
    ProgramData.active_tourney.current_race_data["runs"] = request.json

    # Update the OBS displays
    ProgramData.obs_handler.set_race_time(
        1, pad_decimals(ProgramData.active_tourney.get_race_time_from_runs(0))
    )
    ProgramData.obs_handler.set_race_time(
        2, pad_decimals(ProgramData.active_tourney.get_race_time_from_runs(1))
    )

    last_run: list[float, float] = ProgramData.active_tourney.current_race_data["runs"][
        -1
    ]
    ProgramData.obs_handler.set_run_time(1, pad_decimals(last_run[0]))
    ProgramData.obs_handler.set_run_time(2, pad_decimals(last_run[1]))

    return Response(status=204)


@ui_blueprint.route("/next-round", methods=["POST"])
@cross_origin()
def next_round():
    print_request_info(request)

    q = ProgramData.active_tourney.start_new_round()
    # End of round animation for Swiss (SET always returns [] for q[1])
    if q[1]:
        ProgramData.eliminated_racers = [r["name"] for r in q[1].values()]
        requests.post(
            f"http://{SELF_IP}/alert-controller-from-tourney",
            json={
                "message": f"{len(ProgramData.eliminated_racers)} racer(s) have been eliminated. Please activate the end of round animation to display these to the audience."
            },
        )
        ProgramData.obs_handler.clear_eliminated_racer_columns()
        ProgramData.obs_handler.set_scene(obs_scene.round_complete)
    # Switch to SET from Swiss
    if not q[0]:
        ProgramData.SET_tourney.has_been_activated = True
        ProgramData.SET_tourney.load_data_from_swiss(
            ProgramData.swiss_tourney.pypair_tourney.playersDict
        )
        ProgramData.active_tourney = ProgramData.SET_tourney
        ProgramData.active_tourney.start_new_round()
        requests.post(
            f"http://{SELF_IP}/alert-controller-from-tourney",
            json={"message": "Switching to Single Elimination Tourney Mode."},
        )
        ProgramData.swiss_tourney.pypair_tourney.currentRound += 1
        ProgramData.active_tourney.save_internal_data()

    # Handle popups for SET as we approach the end
    if ProgramData.active_tourney == ProgramData.SET_tourney:
        if len(ProgramData.active_tourney.racer_list) == 1:
            requests.post(
                f"http://{SELF_IP}/alert-controller-from-tourney",
                json={"message": f"We're done! The winner is {ProgramData.active_tourney.racer_list[list(ProgramData.active_tourney.racer_list)[0]]}"},
            )   
            ProgramData.active_tourney = None
            return Response(status=204)
        elif len(ProgramData.active_tourney.racer_list) == 2:
            requests.post(
                f"http://{SELF_IP}/alert-controller-from-tourney",
                json={"message": "Now entering the final match!"},
            )
        elif len(ProgramData.active_tourney.racer_list) <= 4 and len(ProgramData.active_tourney.racer_list) > 2:
            requests.post(
                f"http://{SELF_IP}/alert-controller-from-tourney",
                json={"message": "Now entering semi-finals!"},
            )
        elif len(ProgramData.active_tourney.racer_list) <= 8 and len(ProgramData.active_tourney.racer_list) > 4:
            requests.post(
                f"http://{SELF_IP}/alert-controller-from-tourney",
                json={"message": "Now entering quarter-finals!"},
            )

    ProgramData.obs_handler.set_round_number(
        ProgramData.swiss_tourney.pypair_tourney.currentRound
    )

    ProgramData.save_data()

    requests.post(f"http://{SELF_IP}/next-race")

    return Response(status=204)


@ui_blueprint.route("/next-race", methods=["POST"])
@cross_origin()
def next_race():
    print_request_info(request)

    ProgramData.run_count = 0
    ProgramData.left_lane_submitted = False
    ProgramData.right_lane_submitted = False

    need_new_round: bool = ProgramData.active_tourney.start_new_race()
    queue_data: dict[
        str, list[str]
    ] = ProgramData.active_tourney.get_now_racing_and_up_next()
    ProgramData.now_racing = queue_data["now_racing"]
    ProgramData.up_next = queue_data["up_next"]
    ProgramData.obs_handler.set_now_racing(ProgramData.now_racing)
    ProgramData.obs_handler.set_up_next(ProgramData.up_next)
    ProgramData.obs_handler.reset_run_and_race_times()

    if not need_new_round:
        ProgramData.now_racing = ["N/A", "N/A"]
        requests.post(
            f"http://{SELF_IP}/alert-controller-from-tourney",
            json={
                "message": "There are no more races! Please start a new round, then try again."
            },
        )

    if ProgramData.active_tourney == ProgramData.swiss_tourney:
        ProgramData.races_left_in_round = len(ProgramData.swiss_tourney.pypair_tourney.tablesOut)
        ProgramData.players_left = len(ProgramData.swiss_tourney.pypair_tourney.playersDict)
    else:
        ProgramData.races_left_in_round = len(ProgramData.SET_tourney.race_queue)
        ProgramData.players_left = len(ProgramData.SET_tourney.racer_list)

    ProgramData.save_data()

    return Response(status=204)


@ui_blueprint.route("/edit-ignore-incoming-data-from-timer", methods=["POST"])
@cross_origin()
def edit_ignore_incoming_data_from_timer():
    print_request_info(request)

    ProgramData.ignore_incoming_data_from_timer = request.json["value"]

    return Response(status=204)


@ui_blueprint.route("/obs-action", methods=["POST"])
@cross_origin()
def toggle_recording():
    print_request_info(request)

    action: str = request.json["action"]
    if action == "edit_auto_handle_recording":
        if value := request.get_json("value", silent=True):
            ProgramData.auto_handle_recording = value
        else:
            return Response(status=400)
    elif action == "start_recording":
        ProgramData.obs_handler.start_recording()
    elif action == "stop_recording":
        ProgramData.obs_handler.stop_recording()
    elif action == "toggle_recording":
        ProgramData.obs_handler.toggle_recording()
    else:
        Response(status=400)

    return Response(status=204)


@ui_blueprint.route("/set-obs-scene", methods=["POST"])
@cross_origin()
def set_obs_scene():
    print_request_info(request)

    scene_name: str = request.json["scene_name"]
    if scene_name not in {
        "blank",
        "fullscreen",
        "basic_camera",
        "advanced_camera",
        "video_playback",
        "round_complete",
        "custom_text",
    }:
        return Response(status=400)

    scene: str = {
        "blank": obs_scene.blank,
        "fullscreen": obs_scene.fullscreen,
        "basic_camera": obs_scene.basic_camera,
        "advanced_camera": obs_scene.advanced_camera,
        "video_playback": obs_scene.fullscreen,
        "round_complete": obs_scene.round_complete,
        "custom_text": obs_scene.custom_text,
    }[scene_name]

    ProgramData.obs_handler.set_scene(scene)

    return Response(status=204)


@ui_blueprint.route("/video-player-action", methods=["POST"])
@cross_origin()
def video_player_action():
    print_request_info(request)

    action: str = request.json["action"]
    if action not in {
        "load_latest_video",
        "toggle_playback",
        "stop",
        "slowdown",
        "next_frame",
        "bring_to_foreground",
        "force_close",
        "open_new",
    }:
        return Response(status=400)

    if action == "bring_to_foreground":
        ProgramData.bring_video_player_to_foreground()
    elif action == "force_close":
        ProgramData.kill_video_player()
    elif action == "open_new":
        ProgramData.start_video_player()
    else:
        requests.post(
            f"http://{VIDEO_PLAYER_IP}/video-player-action", json={"action": action}
        )

    return Response(status=204)


@ui_blueprint.route("/round-complete-animation-action", methods=["POST"])
@cross_origin()
def round_complete_animation_action():
    print_request_info(request)

    action: str = request.json["action"]

    if action == "skip":
        ProgramData.obs_handler.finish_end_of_round_eliminations_animation()
    elif action == "start":
        ProgramData.obs_handler.set_scene(obs_scene.round_complete)
        ProgramData.obs_handler.animate_end_of_round_eliminations(ProgramData.eliminated_racers)
    else:
        return Response(status=400)

    return Response(status=204)


@ui_blueprint.route("/set-custom-text-card", methods=["POST"])
@cross_origin()
def set_custom_text_card():
    print_request_info(request)

    text: str = request.json["text"]
    ProgramData.obs_handler.set_custom_text_card(text)

    return Response(status=204)


@ui_blueprint.route("/blink-board", methods=["POST"])
@cross_origin()
def blink_board():
    print_request_info(request)

    board: str = request.json["board"]
    if board not in {"timer", "motor"}:
        return Response(status=400)

    if board == "timer":
        requests.get(f"http://{TIMER_BOARD_IP}/blink")
    elif board == "motor":
        requests.get(f"http://{MOTOR_BOARD_IP}/blink")

    return Response(status=204)


@ui_blueprint.route("/check-elimination", methods=["POST"])
@cross_origin()
def check_elimination():
    print_request_info(request)

    racer_name: str = request.json["racer_name"]

    query: tinydb.Query = tinydb.Query()

    # Check the player was registered in the first place
    if not ProgramData.active_tourney.starting_racers_list_db.search(query["name"] == racer_name):
        return {"eliminated": None}, 200

    # Will be true if they're still in, false if they're eliminated
    found_racer: bool
    if ProgramData.active_tourney == ProgramData.swiss_tourney:
        found_racer = any(
            value["name"] == racer_name
            for value in ProgramData.swiss_tourney.pypair_tourney.playersDict.values()
        )
    else:
        found_racer = racer_name in ProgramData.SET_tourney.racer_list.values()

    return ({"eliminated": False}, 200) if found_racer else ({"eliminated": True}, 200)
