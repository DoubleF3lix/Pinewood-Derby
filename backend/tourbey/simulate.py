from single_elimination import SETTourney
from swiss import SwissTourney

SECS_PER_RUN = 30

# Swiss Tourney Code
swiss_tourney = SwissTourney(no_IO=True)
swiss_tourney.load_players_from_file()
while swiss_tourney.simulate_round():
    pass
print(f"All the rounds are done! Have some stats:\n{len(swiss_tourney.pypair_tourney.playersDict)} players remaining\n{swiss_tourney.pypair_tourney.currentRound} rounds run\n{len(swiss_tourney.race_history_db)} runs run. Assuming {SECS_PER_RUN * 2} seconds per race ({SECS_PER_RUN} per run), that's...\n\t- {len(swiss_tourney.race_history_db) * SECS_PER_RUN * 2} seconds\n\t- {len(swiss_tourney.race_history_db) * SECS_PER_RUN * 2 / 60} minutes\n\t- {round(len(swiss_tourney.race_history_db) * SECS_PER_RUN * 2 / 60 / 60, 2)} hours")
# swiss_tourney.save_internal_data()

print("\n---SWITCHING TO SET---\n")

# SET Code
SET_tourney = SETTourney(no_IO=True)
SET_tourney.load_data_from_swiss(swiss_tourney.pypair_tourney.playersDict)
while SET_tourney.simulate_round():
    pass
print(f"We have a winner! {SET_tourney.racer_list=}\n{SET_tourney.final_player_rankings=}")
# SET_tourney.save_internal_data()
