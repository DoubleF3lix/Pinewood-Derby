import random
import time

import tinydb

try:
    from tourbey.base_tourney import BaseTourney
except ImportError:
    from base_tourney import BaseTourney


class SETTourney(BaseTourney):
    def __init__(self, no_IO: bool = False) -> None:
        self.no_IO = no_IO

        self.db = tinydb.TinyDB("SET_db.json")

        # For archival
        self.starting_racers_list_db = self.db.table("starting_racers_list")

        # Should be appended to by the function that handles race ending
        self.race_history_db = self.db.table("race_history")

        # SET form of pypair's tablesOut
        self.race_queue_db = self.db.table("race_queue")

        # Basically just stores a copy of playersDict, which is removed from as players are eliminated
        self.tourney_data_db = self.db.table("tourney_data")

        # Stores the order in which people are eliminated
        self.final_player_rankings_db = self.db.table("final_player_rankings")

        self.racer_list: dict = {}
        # racers is a list of ints, not strings, runs is a list of list of floats, for times per run
        self.current_race_data: dict[str, list] = {"racers": [], "runs": []}
        # now_racing should be grabbed from self.current_race_data
        # self.up_next names should be fetched from a function
        self.up_next: list[int, int] = [-1, -1]
        self.race_queue: list[list[int, int]] = []
        # Dictionary of player name to their final ranking
        self.final_player_rankings: dict[str, int] = {}

        # Not the actual round count, just how many passes of rounds we've made
        self.elimination_round_count: int = 0

        # Used to keep track of which tournament should be the active one
        self.has_been_activated: bool = False

    def load_data_from_swiss(self, playersDict: dict[int | str, object]):
        self.has_been_activated = True

        # If the keys are str, convert them to int
        # Should only be the case if passed in for testing, but I don't feel like converting it
        playersDict = {int(k): v for k, v in playersDict.items()}

        # Nuke any old data
        self.starting_racers_list_db.truncate()
        self.race_history_db.truncate()

        # Shuffle the input players dict so that the order of the racers is random
        playersDictList = list(playersDict.items())
        random.shuffle(playersDictList)
        playersDict = dict(playersDictList)

        # Populate both the starting racer list and the internal list of non-eliminated racers
        for key, value in playersDict.items():
            self.starting_racers_list_db.insert(
                {"id": key, "name": value["name"], "points": value["points"]}
            )
            self.racer_list[key] = value["name"]

        self.save_internal_data()

    # Dumps the data from the tournament into a JSON file
    def save_internal_data(self) -> None:
        if not self.no_IO:
            self.race_queue_db.truncate()
            self.race_queue_db.insert({"rounds": self.race_queue})

            self.final_player_rankings_db.truncate()
            self.final_player_rankings_db.insert(self.final_player_rankings)

            self.tourney_data_db.truncate()
            self.tourney_data_db.insert({"racer_list": self.racer_list, "current_race_data": self.current_race_data, "up_next": self.up_next, "has_been_activated": self.has_been_activated})

    def load_internal_data(self) -> None:
        self.race_queue = self.race_queue_db.all()[0]["rounds"]

        tourney_data = self.tourney_data_db.all()[0]
        # Puts the racer_list keys back as ints
        tourney_data["racer_list"] = {
            int(k): v for k, v in tourney_data["racer_list"].items()
        }  # Shout out to copilot for writing this so I didn't have to
        self.racer_list = tourney_data["racer_list"]

        self.current_race_data = tourney_data["current_race_data"]
        self.up_next = tourney_data["up_next"]
        self.has_been_activated = tourney_data["has_been_activated"]

    def pair_round(self) -> None:
        player_ids = list(self.racer_list) # list(dict) returns keys

        # Needs to do the amount of races it takes to get it to a power of 2
        # AKA 11 people needs to be reduced to 8, 9 to 8, 7 to 4, etc.
        # And because all races are 2 people, the amount of races needed to get there 
        # is just racer_count - next_power_of_two(racer_count)
        # Because this normalizes the list to a power of 2, this should only run once per tournament
        # After that, you're guaranteed you'll always be left with an even number of players at the end of each round

        # This checks if the number is not a power of two (https://stackoverflow.com/a/57025941)
        if not (len(player_ids) & (len(player_ids) - 1) == 0 and player_ids):
            # https://stackoverflow.com/a/3797818
            next_round_race_count_target = len(player_ids) - 2 ** (len(player_ids).bit_length() - 1)

            # So if the above says we need 3 races, then we need 6 players, so pull them out
            racers_in_next_round = player_ids[-(next_round_race_count_target * 2):]
            # Then chunk them into pairs
            self.race_queue = [
                racers_in_next_round[i : i + 2] for i in range(0, len(racers_in_next_round), 2)
            ]
        else:
            # Chunk the list into pairs, so now we have our rounds
            self.race_queue = [
                player_ids[i : i + 2] for i in range(0, len(player_ids), 2)
            ]

        self.save_internal_data()

    # Always returns [True, []] for parity
    def start_new_round(self) -> list[True, list[None]]:
        self.elimination_round_count += 1

        # Report the last race if there was one
        if self.current_race_data["runs"]:
            try:
                self.report_race()
            # I goofed and added some race data when there wasn't an active race
            except IndexError:
                self.current_race_data["runs"] = []

        # Start fresh
        self.current_race_data = {"racers": [], "runs": []}

        self.pair_round()

        return True, []

    # Returns False if we should start a new round, otherwise returns True
    def start_new_race(self) -> bool:
        # Report the last race if there was one
        if self.current_race_data["runs"]:
            try:
                self.report_race()
            # I goofed and added some race data when there wasn't an active race
            except IndexError:
                self.current_race_data["runs"] = []

        if not self.race_queue:
            return False

        # Get the first item in the race queue out and store it in the current race data (also acts as the Now Racing list)
        self.current_race_data["racers"] = self.race_queue[0]

        # If there's another race to set the Up Next of, do so
        self.up_next = self.race_queue[1] if len(self.race_queue) > 1 else [-1, -1]

        return True

    # Returns the amount of players left. Should be checked when the race is reported by clicking "New Race". If it returns 1, the event is over.
    def report_race(self) -> int:
        racer_one_total_time = self.get_race_time_from_runs(0)
        racer_two_total_time = self.get_race_time_from_runs(1)

        # We keep the current race in the list, so now we need to remove it when we report on it
        del self.race_queue[0]

        # Offset racer one time if they're equal to act as a coin toss
        if racer_one_total_time == racer_two_total_time:
            print(f"{self.current_race_data['players']=} Doing a coin flip to decide the winner. [{racer_one_total_time}/{racer_two_total_time}]")
            # Add or subtract a 10 millisecond difference as a coin toss
            racer_one_total_time += (1 if random.random() < 0.5 else -1) * 0.01

        # The loser is the player with the higher total time
        losing_player_id: int = self.current_race_data["racers"][int(racer_one_total_time < racer_two_total_time)]

        # The placement is just the current length before we delete them
        self.final_player_rankings[len(self.racer_list)] = self.racer_list[losing_player_id]

        # Remove the loser from the racer list
        del self.racer_list[losing_player_id]

        # Add the race to the history
        self.race_history_db.insert(self.current_race_data | {"logged_at": time.strftime("%Y-%m-%d %I:%M:%S %p"), "elimination_round_count": self.elimination_round_count})

        # Reset for the next race
        self.current_race_data = {"racers": [], "runs": []}

        if len(self.racer_list) == 1:
            # Add the last player to the rankings
            self.final_player_rankings[1] = next(iter(self.racer_list.items()))[1]
            self.save_internal_data()
            return

        self.save_internal_data()

        return len(self.racer_list)

    def simulate_round(self) -> bool:
        """
        Usage:
        while tourney.simulate_round():
            pass
        """
        self.start_new_round()
        keep_going = True
        # Need to make a copy since we modify the list as we run through it, meaning we sometimes skip some
        for _ in self.race_queue.copy():
            self.start_new_race()

            self.current_race_data["runs"] = [[1, 2]]
            keep_going: bool = self.report_race()

        return keep_going

# fmt: off
playersDict = {1: {"name": "Player 1", "points": 1}, 2: {"name": "Player 2", "points": 2}, 3: {"name": "Player 3", "points": 3}, 4: {"name": "Player 4", "points": 4}, 5: {"name": "Player 5", "points": 5}, 6: {"name": "Player 6", "points": 6}, 7: {"name": "Player 7", "points": 7}, 8: {"name": "Player 8", "points": 8}, 9: {"name": "Player 9", "points": 9}, 10: {"name": "Player 10", "points": 10}, 11: {"name": "Player 11", "points": 11}, 12: {"name": "Player 12", "points": 12}}
# fmt: on

if __name__ == "__main__":
    tourney = SETTourney()
    tourney.load_data_from_swiss(playersDict)

    while tourney.simulate_round():
        pass

    print(f"We have a winner! {tourney.racer_list=}\n{tourney.final_player_rankings=}")

    tourney.save_internal_data()
