# General config
DEBUG = True
DISABLE_BOARD_COMMUNICATION = False
ENABLE_STREAMING = False

# IP Config
TIMER_BOARD_IP = "192.168.132.180"
MOTOR_BOARD_IP = "192.168.132.181"
SELF_IP = "192.168.132.106:3000"
VIDEO_PLAYER_IP = "192.168.132.106:8000"

# Tourney config
# Elimination will kick after this round number is over (2 is a good idea)
QUALIFIER_ROUND_COUNT = 2
# These two are likely not needed
MIN_PLAYERS_FOR_SWISS_TO_SET = 12
MAX_ROUNDS_FOR_SWISS_TO_SET = 8

DELAY_FOR_AUTO_START_RECORDING = 2
# EDIT VIDEOS_DIR IN misc\video_player.py AS WELL (NVM it's deprecated lol)
