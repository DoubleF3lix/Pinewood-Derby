import contextlib
import random
import statistics
import time

import tinydb

try:
    from const import *
    from tourbey.base_tourney import BaseTourney
    from tourbey.pypair import Tournament
except ImportError:
    from base_tourney import BaseTourney
    from pypair import Tournament

    # This CONST copying sucks but oh well
    QUALIFIER_ROUND_COUNT = 2
    MIN_PLAYERS_FOR_SWISS_TO_SET = 12
    MAX_ROUNDS_FOR_SWISS_TO_SET = 8


class SwissTourney(BaseTourney):
    def __init__(self, no_IO: bool = False) -> None:
        self.no_IO = no_IO

        self.pypair_tourney = Tournament()

        self.db = tinydb.TinyDB("swiss_db.json")

        # For archival
        self.starting_racers_list_db = self.db.table("starting_racers_list")

        # Should be appended to by the function that handles race ending
        self.race_history_db = self.db.table("race_history")

        # Stores pypair internal data. Race queue is handled here as well.
        self.tourney_data_db = self.db.table("pypair_tourney_data")
        # Stores current_race_data and up_next
        self.misc_data_db = self.db.table("misc_data")

        # players is a list of ints, not strings, runs is a list of list of floats, for times per run
        self.current_race_data: dict[str, list] = {"racers": [], "runs": []}

        # now_racing should be grabbed from self.current_race_data
        # self.up_next names should be fetched from a function
        self.up_next: list[int, int] = [-1, -1]

    # Should be called when the tourney is first created
    def load_players_from_file(self):
        # Nuke any old data
        self.starting_racers_list_db.truncate()
        self.race_history_db.truncate()

        # This will be true if the table is empty
        with open("racer_list.txt", "r") as infile:
            for index, line in enumerate(infile.readlines()):
                stripped_line = line.strip()
                # Populate the starting racer list and the internal list of non-eliminated racers
                self.pypair_tourney.addPlayer(index + 1, stripped_line)
                self.starting_racers_list_db.insert(
                    {"id": index + 1, "name": stripped_line}
                )

    # Dumps the data from the tournament into a JSON file
    def save_internal_data(self) -> None:
        if not self.no_IO:
            self.tourney_data_db.truncate()
            self.tourney_data_db.insert(self.pypair_tourney.__dict__)

            self.misc_data_db.truncate()
            self.misc_data_db.insert(
                {"current_race_data": self.current_race_data, "up_next": self.up_next}
            )

    def load_internal_data(self) -> None:
        # playersDict, roundPairings, and countPoints store their keys as ints,
        # but this isn't supported by JSON, so we need to put it back
        tourney_data = self.tourney_data_db.all()[0]
        for key in ["playersDict", "roundPairings", "countPoints"]:
            # Keys may not exist
            # For instance, countPoints doesn't at the start of a match
            with contextlib.suppress(KeyError):
                tourney_data[key] = {
                    int(k): v for k, v in tourney_data[key].items()
                }  # Shout out to copilot for writing this so I didn't have to

        self.pypair_tourney.__dict__ = tourney_data

        misc_data = self.misc_data_db.all()[0]
        self.current_race_data = misc_data["current_race_data"]
        self.up_next = misc_data["up_next"]

    # Removes entries from self.tourney.playersDict if their score is below the median for all players still left
    # Modifies the variable in place, returns the players who were eliminated
    def trim_players(self) -> dict:
        # Cut off all players below the median
        POINTS_BELOW_MEDIAN = 0

        # Calculate the required score to be included
        required_score = (
            statistics.median(
                sorted(
                    [
                        data["points"]
                        for data in self.pypair_tourney.playersDict.values()
                    ]
                )
            )
            - POINTS_BELOW_MEDIAN
        )

        # Use q[1] since that's the data from items()
        trimmed_players = dict(
            filter(
                lambda q: q[1]["points"] >= required_score,
                self.pypair_tourney.playersDict.items(),
            )
        )

        eliminated_players = dict(
            filter(
                lambda q: q[1]["points"] < required_score,
                self.pypair_tourney.playersDict.items(),
            )
        )

        # Put the simplified trimmed players dictionary into the format that pypair needs
        racer_ids = trimmed_players.keys()
        new_racer_data = {}
        for id, data in trimmed_players.items():
            # Remove opponents that are no longer in the tournament
            new_opponents = [
                opponent for opponent in data["opponents"] if opponent in racer_ids
            ]
            data["opponents"] = new_opponents
            new_racer_data[id] = data

        # Replace the old data with the new data
        self.pypair_tourney.playersDict = new_racer_data

        return eliminated_players

    def pair_round(self) -> None:
        # Auto-increments self.pypair_tourney.currentRound
        self.pypair_tourney.pairRound()
        self.save_internal_data()

    # Returns False if we should switch to SET, otherwise returns True
    def start_new_round(self) -> bool:
        # Report the last race if there was one
        if self.current_race_data["runs"]:
            try:
                self.report_race()
            # I goofed and added some race data when there wasn't an active race
            except IndexError:
                self.current_race_data["runs"] = []

        # Start fresh
        self.current_race_data = {"racers": [], "runs": []}

        eliminated_players: list | None = None
        if (
            self.pypair_tourney.currentRound
            > QUALIFIER_ROUND_COUNT
        ):
            eliminated_players = self.trim_players()

        if (
            len(self.pypair_tourney.playersDict) <= MIN_PLAYERS_FOR_SWISS_TO_SET
            or self.pypair_tourney.currentRound > MAX_ROUNDS_FOR_SWISS_TO_SET
        ):
            return False, eliminated_players

        self.pair_round()
        # self.start_new_race()

        return True, eliminated_players

    # Returns False if we should start a new round, otherwise returns True
    def start_new_race(self) -> bool:
        # Report the last race if there was one
        if self.current_race_data["runs"]:
            try:
                self.report_race()
            # I goofed and added some race data when there wasn't an active race
            except IndexError:
                self.current_race_data["runs"] = []

        if not self.pypair_tourney.tablesOut:
            return False

        # Get the first item in the race queue out and store it in the current race data (also acts as the Now Racing list)
        self.current_race_data["racers"] = self.pypair_tourney.roundPairings[
            self.pypair_tourney.tablesOut[0]
        ]

        # If there's another race to set the Up Next of, do so
        self.up_next = (
            self.pypair_tourney.roundPairings[self.pypair_tourney.tablesOut[1]]
            if len(self.pypair_tourney.tablesOut) > 1
            else [-1, -1]
        )

        return True

    def report_race(self) -> None:
        racer_one_total_time = self.get_race_time_from_runs(0)
        racer_two_total_time = self.get_race_time_from_runs(1)

        # Offset racer one time if they're equal to act as a coin toss
        if racer_one_total_time == racer_two_total_time:
            print(
                f"{self.current_race_data['players']=} Doing a coin flip to decide the winner. [{racer_one_total_time}/{racer_two_total_time}]"
            )
            # Add or subtract a 10 millisecond difference as a coin toss
            racer_one_total_time += (1 if random.random() < 0.5 else -1) * 0.01

        # Pypair uses the higher input as the winner, when we want the lower, so we'll use a 1/0 list to report and then the times for the history
        pypair_report_list = [[1, 0], [0, 1]][
            int(racer_one_total_time > racer_two_total_time)
        ]
        self.pypair_tourney.reportMatch(
            self.pypair_tourney.tablesOut[0], pypair_report_list
        )

        # Add the race to the history
        self.race_history_db.insert(
            self.current_race_data
            | {
                "logged_at": time.strftime("%Y-%m-%d %I:%M:%S %p"),
                "elimination_round_count": self.pypair_tourney.currentRound,
            }
        )

        # Reset for the next race
        self.current_race_data = {"racers": [], "runs": []}

        self.save_internal_data()

    def simulate_round(self) -> bool:
        """
        Usage:
        while tourney.simulate_round():
            pass
        """
        if self.start_new_round()[0]:
            # Need to make a copy since we modify the list as we run through it, meaning we sometimes skip some
            for _ in self.pypair_tourney.tablesOut.copy():
                self.start_new_race()
                self.current_race_data["runs"] = [[1, 2]]
                self.report_race()
            return True
        return False


if __name__ == "__main__":
    tourney = SwissTourney()
    tourney.load_players_from_file()

    while tourney.simulate_round():
        pass

    print(
        f"All the rounds are done! Have some stats:\n{len(tourney.pypair_tourney.playersDict)} players remaining\n{tourney.pypair_tourney.currentRound} rounds run\n{len(tourney.race_history_db)} races run. Assuming 50 seconds per round, that's...\n\t- {len(tourney.race_history_db) * 50} seconds\n\t- {len(tourney.race_history_db) * 50 / 60} minutes\n\t- {round(len(tourney.race_history_db) * 50 / 60 / 60, 2)} hours"
    )
    tourney.save_internal_data()
