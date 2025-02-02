import itertools

import tinydb
from tinydb import where


def flatten_list(q: list) -> list:
    return list(itertools.chain(*q))

def dedupe_list(q: list) -> list:
    return list(set(q))


swiss_db = tinydb.TinyDB("swiss_db.json")
set_db = tinydb.TinyDB("SET_db.json")

racers_list = swiss_db.table("starting_racers_list")

swiss_race_history = swiss_db.table("race_history").all()
SET_race_history = set_db.table("race_history").all()

final_player_rankings = dict(set_db.table("final_player_rankings").all()[0])

run_times = dedupe_list(flatten_list(flatten_list([q["runs"] for q in swiss_race_history]) + flatten_list([q["runs"] for q in SET_race_history])))
run_times.sort()
top_times = dict((q, []) for q in run_times[:5])

racer_time_avgs = {}

# This is terrible code, but it works
for race in swiss_race_history + SET_race_history:
    # Turn [[1, 2], [1, 2]] into [[1, 1], [2, 2]]
    organized_by_racer_runs = [[q[0] for q in race["runs"]], [q[1] for q in race["runs"]]]
    # Loop over them, keeping in mind that racers are stored with ["racer0", "racer1"], and racer0's times are stored in the first index of [[1, 1], [2, 2]]
    for racer_index, racer_runs in enumerate(organized_by_racer_runs):
        racer_name = racers_list.get(where("id") == race["racers"][racer_index])["name"]

        if racer_name not in racer_time_avgs:
            racer_time_avgs[racer_name] = [0, 0]

        for time in racer_runs:
            racer_time_avgs[racer_name][0] += time
            racer_time_avgs[racer_name][1] += 1
            if time in top_times:
                top_times[time].append(racer_name)


with open("final_results.txt", "w") as outfile:
    print("Final Rankings\n", file=outfile)
    for ranking, name in dict(reversed(final_player_rankings.items())).items():
        print(f"{ranking}. {name}", file=outfile)

    print("\n-------\n", file=outfile)
    print("\n".join([
        "Awards\n",
        "Originality: TODO",
        "Creativity: TODO",
        "Craftsmanship: TODO"
    ]), file=outfile)
    print("\n-------\n", file=outfile)

    print("Top Times\n", file=outfile)
    for time, racers in top_times.items():
        print(f"{time}s - {', '.join(racers)}", file=outfile)

for name, data in racer_time_avgs.items():
    racer_time_avgs[name] = round(data[0] / data[1], 2)
racer_time_avgs = {k: v for k, v in sorted(racer_time_avgs.items(), key=lambda item: item[1])}
print(racer_time_avgs)
print(list(racer_time_avgs.keys()).index("Racer Name"))
