import sys
import threading
import time

import waitress
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

try:
    from misc.video_player import Player
except ImportError:
    from video_player import Player

app = Flask(__name__)
video_player: Player = None
qapp: QtWidgets.QApplication = None
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/video-player-action", methods=["POST"])
@cross_origin()
def video_player_action():
    print(
        f"[{time.strftime('%m/%d/%Y %r')}] {request.method} {request.path} - {request.remote_addr} - {request.get_json(silent=True)}"
    )

    action: str = request.json["action"]
    if action not in {
        "load_latest_video",
        "toggle_playback",
        "stop",
        "slowdown",
        "next_frame",
    }:
        return Response(status=400)

    # Clicks are emulated since sometimes it freezes if you call the functions manually
    if action == "load_latest_video":
        video_player.openlastvideobutton.click()
        print("Done???")
    elif action == "toggle_playback":
        video_player.playbutton.click()
    elif action == "stop":
        video_player.stopbutton.click()
    elif action == "slowdown":
        video_player.set_playback_speed(10)
    elif action == "next_frame":
        video_player.nextframebutton.click()

    return Response(status=204)


def flask_app():
    print("Serving...")
    waitress.serve(app, host="192.168.132.105", port=8000)


def ui():
    # It's a dirty hack but it works
    global video_player
    global qapp

    qapp = QtWidgets.QApplication(sys.argv)
    video_player = Player()
    video_player.showMaximized()
    sys.exit(qapp.exec_())


if __name__ == "__main__":
    flask_app_thread = threading.Thread(target=flask_app)
    # ui_thread = threading.Thread(target=ui)

    flask_app_thread.start()
    # ui_thread.start()
    ui()
