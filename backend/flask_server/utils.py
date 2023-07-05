import time

from flask import Request

from const import *
from data import ProgramData


# [Month/Day/Year Hour:Minute:Second (A/P)M] [Method (GET/POST/...)] [endpoint] - [Requesting IP] - [JSON Data]
def print_request_info(request: Request) -> None:
    if DEBUG:
        print(
            f"[{time.strftime('%m/%d/%Y %r')}] {request.method} {request.path} - {request.remote_addr} - {request.get_json(silent=True)}"
        )


def bring_video_player_to_foreground() -> None:
    ProgramData.window_manager.find_window_wildcard("Video Player")
    ProgramData.window_manager.set_foreground()


def pad_decimals(num: float) -> str:
    return "{:.2f}".format(num) if num is not None else None
