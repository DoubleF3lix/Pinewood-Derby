fetchRaceData();

setInterval(async () => {
    const checkControllerAlert = await network.get(`http://${BASE_IP}/check-controller-alert`);
    if (checkControllerAlert) {
        showPopup("The emcee has sent an alert and requires your attention.\nPlease advise.", () => { }, true);
        await network.post(`http://${BASE_IP}/clear-controller-alert`)
    }

    const checkControllerFromTourneyAlert = await network.get(`http://${BASE_IP}/check-controller-alert-from-tourney`);
    if (checkControllerFromTourneyAlert.length !== 0) {
        showPopup(`${checkControllerFromTourneyAlert[0]}`, async () => { await network.post(`http://${BASE_IP}/clear-controller-alert-from-tourney`) }, true);
    }

    const checkShouldRefreshTable = await network.get(`http://${BASE_IP}/check-should-refresh-table`);
    if (checkShouldRefreshTable) {
        await fetchRaceData();
        await network.post(`http://${BASE_IP}/clear-should-refresh-table`)
    }

    const checkCarsReady = await network.get(`http://${BASE_IP}/check-cars-ready`);
    document.getElementById("markStartReadyButton").disabled = !checkCarsReady;
}, 1000)

function addRunToRaceTable(racer1Time, racer2Time) {
    const table = document.getElementById("raceDataTable");
    const rowCount = table.rows.length;
    const newRow = table.insertRow(rowCount);

    // const runNumCell = newRow.insertCell(0);
    // runNumCell.textContent = (rowCount + 1).toString();

    // Create the base input box for both columns
    const racerCellInput = document.createElement("input");
    racerCellInput.classList.add("textbox", "noSpin")
    racerCellInput.type = "number";
    racerCellInput.pattern = "[\d.]*";

    // Apply said input box to both columns with proper values
    const racer1Cell = newRow.insertCell(0);
    const racer1CellInput = racerCellInput.cloneNode();
    racer1CellInput.value = racer1Time.toString();
    racer1Cell.appendChild(racer1CellInput);

    const racer2Cell = newRow.insertCell(1);
    const racer2CellInput = racerCellInput.cloneNode();
    racer2CellInput.value = racer2Time.toString();
    racer2Cell.appendChild(racer2CellInput);

    const removeRunCell = newRow.insertCell(2);
    const removeRunCellButton = document.createElement("button");
    removeRunCellButton.classList.add("standardButton", "inline", "textboxButton");
    removeRunCellButton.textContent = "Remove";
    removeRunCellButton.onclick = function () { removeRaceDataRow(this); };
    removeRunCell.appendChild(removeRunCellButton);
}

function getRaceDataFromRaceTable() {
    let output = [];
    for (const row of document.getElementById("raceDataTable").rows) {
        let rowCells = row.cells;
        // children access index is guaranteed to be 0 since I never plan on having more than one child in the cell
        let dataCells = [Number(rowCells[0].children[0].value) || null, Number(rowCells[1].children[0].value) || null];
        // Run Number as key
        output.push(dataCells);
    }
    return output;
}

async function updateRaceData() {
    await network.post(
        `http://${BASE_IP}/update-race-data`,
        getRaceDataFromRaceTable()
    );
}

async function fetchRaceData() {
    // Remove the old table data
    let rows = document.getElementById("raceDataTable").rows;
    while (rows.length > 0) {
        rows[0].parentNode.removeChild(rows[0]);
    }

    const data = await network.get(`http://${BASE_IP}/get-race-data`, false);
    const runs = data["runs"];

    if (runs.length > 0) {
        for (const run of runs) {
            addRunToRaceTable(run[0] != null ? run[0] : "NF", run[1] != null ? run[1] : "NF");
        }
    }
}

function removeRaceDataRow(buttonClicked) {
    // Updating should be done by clicking the button
    buttonClicked.parentElement.parentElement.remove();
}

async function nextRound() {
    showPopup(
        "Are you sure you want to start a new round?<br>The current round may not be finished yet!",
        async function () {
            await network.post(`http://${BASE_IP}/next-round`);
            // showPopup("New round started! Make sure to use \"Next Race\" to start the first race.", () => { }, true);
        }
    );
}

async function nextRace() {
    let runCount = Object.keys(getRaceDataFromRaceTable()).length;
    if (runCount < 2) {
        showPopup(
            `Are you sure you want to start a new race?<br>${runCount == 0 ? "No runs have" : "Only one run has"} been recorded!`,
            async function () {
                await network.post(`http://${BASE_IP}/next-race`);
            }
        );
    } else {
        await network.post(`http://${BASE_IP}/next-race`);
    }
}

async function markStartReady() {
    await network.post(`http://${BASE_IP}/give-start-approval`);
}

async function manuallyStartMotor(silent) {
    showPopup(
        "Are you sure you want to manually start the motor?",
        async function () {
            await network.post(`http://${BASE_IP}/force-spin-motor`, { "silent": silent });
        }
    );
}

async function editIgnoreIncomingDataFromTimer(value) {
    await network.post(`http://${BASE_IP}/edit-ignore-incoming-data-from-timer`, { "value": value });
}

async function markLaneFinish(lane) {
    showPopup(
        `Are you sure you want to mark the ${lane == 1 ? "left" : "right"} lane as finished?`,
        async function () {
            await network.post(`http://${BASE_IP}/mark-finish`, { "lane": lane });
        }
    )
}

async function markLaneFail(lane) {
    showPopup(
        `Are you sure you want to mark the ${lane == 1 ? "left" : "right"} lane as a fail?`,
        async function () {
            await network.post(`http://${BASE_IP}/mark-fail`, { "lane": lane });
        }
    )
}

async function setLanePosition(lane, buttonClicked) {
    let value = buttonClicked.previousElementSibling.value;

    await network.post(`http://${BASE_IP}/set-lane-position`, { "lane": lane, "value": value });

    if (document.getElementById("autoShowTimerOnFinish").checked) {
        await network.post(`http://${BASE_IP}/edit-lane-position-visibility`, { "lane": lane, "visibility": true })
    }
}

async function setLaneRunTime(lane, buttonClicked) {
    let value = buttonClicked.previousElementSibling.value;

    // * 1000 because the server expects milliseconds
    await network.post(`http://${BASE_IP}/set-lane-run-time`, { "lane": lane, "value": value * 1000 });

    if (document.getElementById("autoShowTimerOnFinish").checked) {
        await network.post(`http://${BASE_IP}/edit-lane-run-time-visibility`, { "lane": lane, "visibility": true })
    }
}

async function editShowTimeOnFinish(value) {
    await network.post(`http://${BASE_IP}/edit-show-time-on-finish`, { "value": value });
}

async function editLanePositionVisibility(lane, visibility) {
    await network.post(`http://${BASE_IP}/edit-lane-position-visibility`, { "lane": lane, "visibility": visibility });
}

async function editLaneRunTimeVisibility(lane, visibility) {
    await network.post(`http://${BASE_IP}/edit-lane-run-time-visibility`, { "lane": lane, "visibility": visibility });
}

const obsControls = {
    startRecording: async function () {
        await network.post(`http://${BASE_IP}/obs-action`, { "action": "start_recording" });
    },
    stopRecording: async function () {
        await network.post(`http://${BASE_IP}/obs-action`, { "action": "stop_recording" });
    },
    toggleRecording: async function () {
        await network.post(`http://${BASE_IP}/obs-action`, { "action": "toggle_recording" });
    },
    editAutoHandleRecording: async function (value) {
        await network.post(`http://${BASE_IP}/obs-action`, { "action": "edit_auto_handle_recording", "value": value });
    },
    setScene: async function (sceneName) {
        await network.post(`http://${BASE_IP}/set-obs-scene`, { "scene_name": sceneName });
    },
    setCustomTextCard: async function () {
        await network.post(`http://${BASE_IP}/set-custom-text-card`, { "text": document.getElementById("customTextInput").value });
    }
};

const videoPlayer = {
    loadLatestVideo: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "load_latest_video" });
    },
    togglePlayback: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "toggle_playback" });
    },
    stopVideo: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "stop" });
    },
    slowdownVideo: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "slowdown" });
    },
    nextFrame: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "next_frame" });
    },
    forceClose: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "force_close" });
    },
    openNew: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "open_new" });
    },
    bringToForeground: async function () {
        await network.post(`http://${BASE_IP}/video-player-action`, { "action": "bring_to_foreground" });
    }
};

const roundCompleteAnimation = {
    play: async function () {
        await network.post(`http://${BASE_IP}/round-complete-animation-action`, { "action": "start" });
    },
    skip: async function () {
        await network.post(`http://${BASE_IP}/round-complete-animation-action`, { "action": "skip" });
    }
}

async function alertEmcee() {
    await network.post(`http://${BASE_IP}/alert-emcee`, { "message": document.getElementById("alertEmceeInput").value });
}

async function blinkBoard(board) {
    await network.post(`http://${BASE_IP}/blink-board`, { "board": board });
}