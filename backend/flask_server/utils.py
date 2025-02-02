import time

import requests
from flask import Request

from const import *
from data import ProgramData


# [Month/Day/Year Hour:Minute:Second (A/P)M] [Method (GET/POST/...)] [endpoint] - [Requesting IP] - [JSON Data]
def print_request_info(request: Request) -> None:
    if DEBUG:
        print(
            f"[{time.strftime('%m/%d/%Y %r')}] {request.method} {request.path} - {request.remote_addr} - {request.get_json(silent=True)}"
        )


def post_request(url: str, data: dict = None, json: dict = None) -> None:
    # Still send self-requests
    if not DISABLE_BOARD_COMMUNICATION or SELF_IP in url:
        requests.post(url, data=data, json=json)
    else:
        print(f"POST Request to board blocked: {url=}, {data=}, {json=}")


# This is only used for board blink... why was that not made a POST?
# Check that, it was so you could manually make it blink by visiting the URL
def get_request(url: str) -> None:
    if not DISABLE_BOARD_COMMUNICATION:
        requests.get(url)
    else:
        print(f"GET Request to board blocked: {url=}")


def bring_video_player_to_foreground() -> None:
    ProgramData.window_manager.find_window_wildcard("Video Player")
    ProgramData.window_manager.set_foreground()


def pad_decimals(num: float) -> str:
    return "{:.2f}".format(num) if num is not None else None
