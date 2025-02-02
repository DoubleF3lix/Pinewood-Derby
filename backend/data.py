import json
import subprocess
import sys
import threading

from const import *
from misc.obs_handler import OBSHandler
from misc.window_manager import WindowManager
from tourbey.single_elimination import SETTourney
from tourbey.swiss import SwissTourney


class ProgramData:
    # Used to keep track of the motor board state
    cars_ready: bool = False
    approval_given: bool = False

    # Queried by the controller and emcee panels respectively
    alert_controller: bool = False  # Controller is just a general alert message
    alert_emcee: str = ""  # Custom message displayed to the emcee
    alert_controller_from_tourney: list = [] # A queue of multiple messages this time since we really don't want to override any
    should_refresh_table: bool = False

    ignore_incoming_data_from_timer: bool = False

    left_lane_submitted: bool = False
    right_lane_submitted: bool = False
    run_count: int = 1

    races_left_in_round: int = 0
    players_left: int = 0

    # Set by the tournament manager queue for display on the emcee and controller panels
    now_racing: list[str, str] = ["N/A", "N/A"]
    up_next: list[str, str] = ["N/A", "N/A"]
    eliminated_racers: list[str] = None

    # Allows the API to access the tournament data
    swiss_tourney: SwissTourney = SwissTourney(no_IO=False)
    SET_tourney: SETTourney = SETTourney(no_IO=False)
    active_tourney: SwissTourney | SETTourney = None

    # Allows the API to access the video player and OBS handler
    # The window manager is used to show the video player at appropriate times
    video_player_process: subprocess.Popen = None
    try:
        obs_handler: OBSHandler = OBSHandler()
    except ConnectionRefusedError:
        print("OBS needs to be open with the WebSocket plugin enabled to run.")
        sys.exit(0)
    window_manager: WindowManager = WindowManager()

    auto_handle_recording: bool = True

    @staticmethod
    def delayed_start_recording(time_delay: int = 2) -> None:
        threading.Timer(time_delay, ProgramData.obs_handler.start_recording).start()

    @staticmethod
    def bring_video_player_to_foreground() -> None:
        ProgramData.window_manager.find_window_wildcard("Video Player")
        ProgramData.window_manager.set_foreground()

    @staticmethod
    def start_video_player() -> None:
        if ProgramData.video_player_process:
            ProgramData.kill_video_player()

        DETACHED_PROCESS = 0x00000008
        # Uses pythonw.exe instead of python.exe
        pythonw = f"{sys.executable[:-4]}w{sys.executable[-4:]}"
        ProgramData.video_player_process = subprocess.Popen(
            [
                pythonw,
                "misc\\video_player_handler.py",
            ],
            creationflags=DETACHED_PROCESS,
        )

    @staticmethod
    def kill_video_player() -> None:
        ProgramData.video_player_process.kill()

    @staticmethod
    def save_data() -> None:
        with open("ProgramData.json", "w") as outfile:
            json.dump({
                "cars_ready": ProgramData.cars_ready,
                "approval_given": ProgramData.approval_given,
                "alert_controller": ProgramData.alert_controller,
                "alert_emcee": ProgramData.alert_emcee,
                "alert_controller_from_tourney": ProgramData.alert_controller_from_tourney,
                "should_refresh_table": ProgramData.should_refresh_table,
                "left_lane_submitted": ProgramData.left_lane_submitted,
                "right_lane_submitted": ProgramData.right_lane_submitted,
                "run_count": ProgramData.run_count,
                "races_left_in_round": ProgramData.races_left_in_round,
                "players_left": ProgramData.players_left,
                "now_racing": ProgramData.now_racing,
                "up_next": ProgramData.up_next,
                "eliminated_racers": ProgramData.eliminated_racers,
            }, outfile, indent=4)

    @staticmethod
    def load_data() -> None:
        try:
            with open("ProgramData.json", "r") as infile:
                data = json.load(infile)
                ProgramData.cars_ready = data["cars_ready"]
                ProgramData.approval_given = data["approval_given"]
                ProgramData.alert_controller = data["alert_controller"]
                ProgramData.alert_emcee = data["alert_emcee"]
                ProgramData.alert_controller_from_tourney = data["alert_controller_from_tourney"]
                ProgramData.should_refresh_table = data["should_refresh_table"]
                ProgramData.left_lane_submitted = data["left_lane_submitted"]
                ProgramData.right_lane_submitted = data["right_lane_submitted"]
                ProgramData.run_count = data["run_count"]
                ProgramData.races_left_in_round = data["races_left_in_round"]
                ProgramData.players_left = data["players_left"]
                ProgramData.now_racing = data["now_racing"]
                ProgramData.up_next = data["up_next"]
                ProgramData.eliminated_racers = data["eliminated_racers"]
        except FileNotFoundError:
            print("Tried to load ProgramData, but JSON file was not found. Ignoring.")
