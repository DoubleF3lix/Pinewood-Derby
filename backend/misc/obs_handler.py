import contextlib
import threading
import time
from typing import Literal

import obsws_python as obsws
import obsws_python.error as obsws_errors
from const import *


# obs.set_current_preview_scene("Round Complete") or set_scene(obs_scene.camera)
class obs_scene:
    blank = "Blank"
    fullscreen = "Fullscreen"
    basic_camera = "Basic Camera View"
    advanced_camera = "Advanced Camera View"
    video_playback = "Video Playback" # Deprecated because video player capturing is wack
    round_complete = "Round Complete"
    custom_text = "Custom Text"


class OBSHandler:
    def __init__(self):
        self.connection = obsws.ReqClient(host="localhost", port=4455)

        self.connection.set_studio_mode_enabled(True)
        self.connection.set_current_program_scene(obs_scene.basic_camera)
        self.connection.set_current_preview_scene(obs_scene.advanced_camera)

        self.is_recording: bool = False
        self.recording_file_name: str = ""

    def first_time_init(self) -> None:
        self.reset_run_and_race_times()

        self.set_now_racing(("N/A", "N/A"))
        self.set_up_next(("N/A", "N/A"))

        self.set_round_number(0)

        self.clear_eliminated_racer_columns()

        self.set_custom_text_card("The event will start soon\n\n\nStop destroying volcanoes to make lava lamps")
        self.set_scene(obs_scene.custom_text)

    def clear_eliminated_racer_columns(self):
        self.set_text("eliminated_racers_column_1", "")
        self.set_text("eliminated_racers_column_2", "")
        self.set_text("eliminated_racers_column_3", "")

    # Alias
    def start_recording(self) -> None:
        # Can happen if the auto handle recording variable changes state mid run
        with contextlib.suppress(obsws_errors.OBSSDKError):
            self.connection.start_record()

    def stop_recording(self) -> None:
        # Can happen if the auto handle recording variable changes state mid run
        with contextlib.suppress(obsws_errors.OBSSDKError):
            self.connection.stop_record()

    def toggle_recording(self) -> None:
        self.connection.toggle_record()

    def set_scene(self, scene: obs_scene) -> None:
        try:
            self.connection.set_current_preview_scene(scene)
        except obsws_errors.OBSSDKError:
            print(
                "ERROR - Internal from obs_handler.set_scene. Make sure the scene exists in OBS, and that Studio Mode is enabled"
            )

    def set_text(self, text_item_name: str, text: str) -> None:
        self.connection.set_input_settings(text_item_name, {"text": text}, True)

    def append_text(
        self, text_item_name: str, text: str, separator: str = "\n"
    ) -> None:
        old_text = self.connection.get_input_settings(text_item_name).input_settings[
            "text"
        ]
        new_text = old_text + separator + text
        self.set_text(text_item_name, new_text)

    # Alias methods
    def set_run_time(self, racer_number: Literal[1, 2], time: float) -> None:
        self.set_text(f"run_time_{racer_number}", str(time) if time is not None else "0.00")

    def set_race_time(self, racer_number: Literal[1, 2], time: float) -> None:
        self.set_text(f"race_time_{racer_number}", str(time) if time is not None else "0.00")

    def reset_run_times(self) -> None:
        self.set_run_time(1, "0.00")
        self.set_run_time(2, "0.00")

    def reset_run_and_race_times(self) -> None:
        self.reset_run_times()

        self.set_race_time(1, "0.00")
        self.set_race_time(2, "0.00")

    def set_now_racing(self, racer_names: tuple[str, str]) -> None:
        self.set_text("now_racing", f"{racer_names[0]} vs. {racer_names[1]}")
        self.connection.set_profile_parameter(
            "Output", "FilenameFormatting", f"{racer_names[0]} vs {racer_names[1]} %CCYY %I-%mm-%ss %p"
        )  # Automatically adds extension

    def set_up_next(self, racer_names: tuple[str, str]) -> None:
        self.set_text("up_next", f"{racer_names[0]} vs. {racer_names[1]}")

    def set_round_number(self, round_number: int) -> None:
        self.set_text("round_number", f"Round {round_number}")
        # - 1 since the counter is already incremented when we're showing (AKA we're on round 3 but it's round 2 end)
        self.set_text("round_complete_text", f"Round {round_number - 1} Complete")

    def set_custom_text_card(self, text: str) -> None:
        self.set_text("custom_text", text)

    def animate_end_of_round_eliminations(
        self, eliminated_racer_names: list[str], time_delay: float = 0.75
    ) -> None:
        self.clear_eliminated_racer_columns()

        # Split the large array of strings into smaller arrays of 3 (one per column)
        # Also, pad the first row so the animation isn't as jarring
        chunked_names = [["", "", ""]] + [
            eliminated_racer_names[x : x + 3]
            for x in range(0, len(eliminated_racer_names), 3)
        ]

        # Pad the last element to be 3 long if it isn't already
        # This is so we don't have to do checking before trying to access an element that doesn't exist
        if len(q := chunked_names[-1]) < 3:
            q += [""] * (3 - len(q))

        # Offload the time delay code to a new thread so it doesn't block everything
        self.keep_animating_eor_eliminations = True
        internal_thread = threading.Thread(
            target=self._animate_end_of_round_eliminations,
            args=(chunked_names, time_delay),
        )
        internal_thread.start()

    def finish_end_of_round_eliminations_animation(self) -> None:
        self.keep_animating_eor_eliminations = False

    def _animate_end_of_round_eliminations(
        self, chunked_names: list[list[str, str]], time_delay: float
    ) -> None:
        first_run = True
        separator = ""

        for chunk in chunked_names:
            self.append_text("eliminated_racers_column_1", chunk[0], separator)
            self.append_text("eliminated_racers_column_2", chunk[1], separator)
            self.append_text("eliminated_racers_column_3", chunk[2], separator)

            # Allows for stopping the animation prematurely
            if self.keep_animating_eor_eliminations:
                time.sleep(time_delay)

            if first_run:
                first_run = False
                separator = "\n"


if __name__ == "__main__":
    obs = OBSHandler()
    obs.first_time_init()
    obs.animate_end_of_round_eliminations(
        [
           "Player 1",
           "Player 2",
           "Player 3",
           "Player 4"
        ],
        1,
    )
    time.sleep(4)
    obs.finish_end_of_round_eliminations_animation()
