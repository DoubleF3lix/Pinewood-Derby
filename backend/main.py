import contextlib
import os

import waitress
from flask import Flask
from flask_cors import CORS

from data import ProgramData
from flask_server import (continuous_endpoints, motor_endpoints,
                          timer_endpoints, ui_endpoints)

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


app.register_blueprint(continuous_endpoints.continuous_blueprint)
app.register_blueprint(motor_endpoints.motor_board_blueprint)
app.register_blueprint(timer_endpoints.timer_board_blueprint)
app.register_blueprint(ui_endpoints.ui_blueprint)


def first_run():
    print("First time loading. Initializing data...")
    ProgramData.active_tourney = ProgramData.swiss_tourney
    ProgramData.swiss_tourney.load_players_from_file()
    ProgramData.swiss_tourney.save_internal_data()

    ProgramData.obs_handler.first_time_init()

    print(
        "Done! Swiss tourney has been set to the active tourney, players have been loaded, round 1 has been started, and the OBS handler has been initialized."
    )


if "INIT" in os.listdir():
    os.remove("INIT")
    first_run()
else:
    print("Loading pre-existing data...")
    # Data may not exist
    with contextlib.suppress(IndexError):
        ProgramData.swiss_tourney.load_internal_data()
        print("Loaded data from Swiss")
    with contextlib.suppress(IndexError):
        ProgramData.SET_tourney.load_internal_data()
        print("Loaded data from SET")

    if ProgramData.SET_tourney.has_been_activated:
        ProgramData.active_tourney = ProgramData.SET_tourney
        print("Set active tourney to SET")
    else:
        ProgramData.active_tourney = ProgramData.swiss_tourney
        print("Set active tourney to Swiss")

    ProgramData.load_data()
 
    # Resetting OBS stuff
    queue_data: dict[
        str, list[str]
    ] = ProgramData.active_tourney.get_now_racing_and_up_next()
    ProgramData.now_racing = queue_data["now_racing"]
    ProgramData.up_next = queue_data["up_next"]
    ProgramData.obs_handler.set_now_racing(ProgramData.now_racing)
    ProgramData.obs_handler.set_up_next(ProgramData.up_next)


print("Serving...")
waitress.serve(app, host="192.168.132.105", port=3000, threads=4)
