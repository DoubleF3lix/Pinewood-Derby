import tinydb
from tinydb.table import Table


class BaseTourney:
    current_race_data: dict[str, list]
    up_next: list
    starting_racers_list_db: Table

    def save_internal_data(self): ...

    def append_run(self, racer_one_time: float = None, racer_two_time: float = None) -> None:
        try:
            last_run = self.current_race_data["runs"][-1]

            # If only racer one is reported and it wasn't reported for the last run, report it for that run instead
            if last_run[0] is None and racer_one_time is not None and racer_two_time is None:
                last_run[0] = racer_one_time
                self.current_race_data["runs"][-1] = last_run
            elif last_run[1] is None and racer_two_time is not None and racer_one_time is None:
                last_run[1] = racer_two_time
                self.current_race_data["runs"][-1] = last_run
            else:
                self.current_race_data["runs"].append([racer_one_time, racer_two_time])
        except IndexError:
            self.current_race_data["runs"].append([racer_one_time, racer_two_time])

        self.save_internal_data()

    def get_names_from_ids(self, ids: list[int]) -> list[str]:
        query: tinydb.Query = tinydb.Query()
        return [
            self.starting_racers_list_db.search(query["id"] == id)[0]["name"]
            if id != -1
            else "N/A"
            for id in ids
        ]

    def get_now_racing_and_up_next(self) -> dict[str, list[str]]:
        output: dict = {"now_racing": ["N/A", "N/A"], "up_next": ["N/A", "N/A"]}
        if q := self.current_race_data["racers"]:
            output["now_racing"] = self.get_names_from_ids(q)
        if q := self.up_next:
            output["up_next"] = self.get_names_from_ids(q)

        return output

    def get_race_time_from_runs(self, lane_ID: int) -> float:
        # Use filter to remove None arguments just in case
        return sum(filter(None, (q[lane_ID] for q in self.current_race_data["runs"])))
