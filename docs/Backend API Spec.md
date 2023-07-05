# Backend API Specification
All requests should be sent with `{"Content-Type": "application/json"}`, unless specified otherwise. 
Furthermore, all requests return `text/json`, unless stated otherwise. If an endpoint is not explicitly stated to return a 2XX code, then it will return 204 unless stated otherwise. All endpoints will return a 400 if required args are missing (or if they're not an expected value), and all args are required unless noted otherwise. Additional arguments will simply be ignored.
All `POST` requests will return 204 unless stated otherwise, and all `GET` requests will return 200 with the request value as a string unless stated otherwise.

# Endpoints
Unlike the motor and timer board APIs, these can be split up into several groups, namely:
- `continuous`: These endpoints are called constantly on a cycle to check some data. As such, these endpoints do not bring their usage to the terminal.
- `motor`: These endpoints are responsible for communicating with the motor board
- `timer`: These endpoints are responsible for communicating with the timer board
- `ui`: These endpoints are related to the UI and its signals.


## Continuous
All alerts in here (except `clear` alerts, which are only in here for organization) are called every second by some panel or device

### GET /check-connectivity
Used by the Motor and Timer boards to make sure they're still connected to the network and can access the backend. Unconditionally returns 204.

### GET /check-emcee-alert
Used by the emcee panel to check if it should display an alert (with custom text content)

Responses:
* 200: A dictionary with a `message` key with a string value of a message if there is one, or `null`.

### POST /clear-emcee-alert
Called by the emcee panel when a shown emcee alert is cleared

### GET /check-controller-alert
Used by the control panel to check if it should display an alert (just a boolean since controller alerts aren't customizable)

Responses:
* 200: Boolean, `true` if it should display an alert

### POST /clear-controller-alert
Called by the control panel when a shown controller alert is cleared

### GET /check-controller-alert-from-tourney
A variation of `/check-controller-alert` that doesn't display the info text saying it came from the emcee, and allows for multiple alerts to be queued

Responses:
* 200: An array of strings, each corresponding to a different alert

### POST /clear-controller-alert-from-tourney
Clears the first queued alert in the list. Called by the control panel when one of the alerts is accepted

### GET /check-should-refresh-table
Set by the backend whenever the race data changes to tell the control panel to refresh the times table

Responses:
* 200: Boolean, `true` if the table should be refreshed

### POST /clear-should-refresh-table
Used by the control panel to indicate that it has received the refresh signal and has acted accordingly

### GET /check-cars-ready
Used by the control panel to disable the `Mark Start Ready` button when the cars are not marked as ready

Responses:
* 200: Boolean, `true` if the cars are ready

### GET /get-race-info
Used by both the emcee and control panels to display race data (Now Racing, Up Next, Races Left in Round, and Players Left)

Responses:
* 200: A dictionary with the following structure (using python's typing system):
```py
{
    "now": list[str, str],
    "next": list[str, str],
    "races_left_in_round": int,
    "players_left": int
}
```


## Motor
Handles all interactions with the motor board (the one at the start of the track). `give-start-approval` and `force-spin-motor` are proxy endpoints that also exist on the motor board. See the motor board API spec for more info.

### POST /cars-ready
Called by the motor board when the button is pressed by the attendant to mark the cars as ready

### POST /give-start-approval
Called by the control panel when the `Mark Start Ready` button is pressed. This relays the signal to the motor board so that the attendant can press the starting button.

Responses:
* 400: Tried to give approval, but the cars were not marked as ready

### POST /force-spin-motor
Forcefully spins the motor, bypassing the need for cars to be marked as ready

Args:
* `silent`: Any value. Just the existence of the argument is checked. If it does exist, the motor board will not call `/run-started`. 

### POST /run-started
Called by the motor board when the run is started (either by the attendant pressing the starting button or by `/force-spin-motor` being called without the `silent` option)


## Timer
All of these endpoints deal with the timer system (at the end of the track), and controlling the displays

### POST /lane-end-triggered
Called from the timer board when a lane laser is tripped. Takes data in as a byte string.

Args:
* `<laneID>&<finishedTime>&<position>&<wasFail>`, where all arguments are integers. `finishedTime` is in milliseconds, `laneID` is `1` for the left lane and `2` for the right, and both `finishedTime` and `position` can be safely ignored if `wasFail` is `1`.

### POST /mark-finish
Proxy endpoint. Called by the control panel to forcefully mark a lane as finished, which is equivalent to tripping the laser.

Args:
* `lane`: Either `1` or `2`, with `1` being the left lane and `2` being the right

### POST /mark-fail
Proxy endpoint. Called by the control panel to mark a lane as a failure (keeps the position display blank and puts FAIL on the time display)

Args:
* `lane`: Either `1` or `2`, with `1` being the left lane and `2` being the right

### POST /set-lane-position
Proxy endpoint. Called by the control panel to manually set the timer board's internal position value.

Args:
* `lane`: Either `1` or `2`, with `1` being the left lane and `2` being the right
* `value`: An integer from 1 to 9 (inclusive)

### POST /set-lane-run-time
Proxy endpoint. Called by the control panel to manually set the timer board's internal timer value.

Args:
* `lane`: Either `1` or `2`, with `1` being the left lane and `2` being the right
* `value`: Integer, the value to set in milliseconds

### POST /edit-show-time-on-finish
Proxy endpoint. Called by the control panel when the checkbox value is changed. Sets whether or not the timer board should show the position and timer values on the displays when a lane's laser is tripped. While the timer board allows for setting this individually per lane, this endpoint sets it for both. See the timer board API spec for more info.

Args:
* `value`: Boolean

### POST /edit-lane-position-visibility
Pseudo-proxy endpoint (the timer board has separate endpoints for hiding and showing, and this endpoint delegates to one of those depending on the `visibility` argument). Called by the control panel when the Show/Hide Position buttons are pressed.

Args:
* `lane`: Either `1` or `2`, with `1` being the left lane and `2` being the right
* `visibility`: Boolean

### POST /edit-lane-run-time-visibility
Pseudo-proxy endpoint (the timer board has separate endpoints for hiding and showing, and this endpoint delegates to one of those depending on the `visibility` argument). Called by the control panel when the Show/Hide Run Time buttons are pressed.

Args:
* `lane`: Either `1` or `2`, with `1` being the left lane and `2` being the right
* `visibility`: Boolean


## UI
These are all of the UI endpoints that don't relate to the motor or timer boards (which is the rest of the backend most of the time)

### POST /alert-controller
Used by the emcee panel to mark that the controller needs to show an alert (this is not customizable and only sets a boolean internally)

### POST /alert-controller-from-tourney
Used by the internal backend to mark that the controller needs to show a new alert (this is customizable and supports a queue of messages)

### POST /alert-emcee
Used by the controller to send a message to the emcee as an alert (this is customizable but subsequence alerts will overwrite each other)

### GET /get-race-data
Used by the control panel to refresh the time table 

Responses:
* 200: A dictionary with a `runs` key with this structure (python's type hinting again): `list[list[int, int]]`

### POST /update-race-data
Overwrites the current race data and refreshes the OBS display. Called by the `Update Race Data` button when changes are made to the table.

Args:
* `list[list[int, int]]`, the same kind of output that `/get-race-data` gives, passed directly as JSON (no dictionary)

### POST /next-round
Used by the control panel when the `Next Round` button is pressed. Manages 60% of the tournament backend.

### POST /next-race
Used by the control panel when the `Next Race` button is pressed. Manages 35% of the tournament backend.

### POST /edit-ignore-incoming-data-from-timer
Called by the control panel when the corresponding checkbox is edited. Makes any calls to `/lane-end-triggered` be ignored.

### POST /obs-action
Called by the control panel. Handles OBS recording.

Args:
* `action`: one of the following:
    * `edit_auto_handle_recording`: Called with this parameter when the corresponding checkbox is changed. When checked, recording automatically starts 2 seconds after `/run-started` is called and stops when both lane ends are triggered.
    * `start_recording`
    * `stop_recording`
    * `toggle_recording`
* `value`: Boolean, optional. Only needed when `action` is `edit_auto_handle_recording`. 

### POST /set-obs-scene
Sets the scene of the OBS instance

Args:
* `scene_name`: one of the following:
    * `blank`
    * `fullscreen`
    * `basic_camera`
    * `advanced_camera`
    * `video_playback`
    * `round_complete`
    * `custom_text`

### POST /video-player-action
Performs an action on the video player (or regarding its existence)

Args:
* `action`, one of:
    * `load_latest_video`
    * `toggle_playback`
    * `stop`
    * `slowdown`
    * `next_frame`
    * `bring_to_foreground`
    * `force_close`
    * `open_new`

### POST /round-complete-animation-action
Performs an action with the round completion animation at the end of a round

Args:
* `action`, one of:
    * `start`, also clears and restarts
    * `skip`, skips to the end

### POST /set-custom-text-card
Sets the text of the `Custom Text` scene in OBS

Args:
* `text`: String, the text to set (normally provided by the textbox above the submit button)

### POST /blink-board
Proxy endpoint (just calls `/blink` on the static IP of the corresponding board). Used for debugging purposes to ensure a good connection with the hardware. 

Args:
* `board`, one of:
    * `timer`
    * `motor`

### POST /check-elimination
Used by the check elimination panel to see if a racer is still in

Args:
* `racer_name`: String, the name of the racer to check the status of

Responses:
* 200: Dictionary, with an `eliminated` key. The value of `eliminated` can be one of three things:
    * `null`: A racer with that name was not found
    * `true`: A racer with that name was found and is not eliminated
    * `false`: A racer with that name was found and is eliminated
