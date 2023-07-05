const racerNames = [
    "Player 1",
    "Player 2",
    "Player 3",
    "Player 4",
    "Player 5",
    "Player 6",
    "Player 7",
    "Player 8",
    "Player 9",
    "Player 10",
    "Player 11",
    "Player 12",
    "Player 13",
    "Player 14",
    "Player 15",
    "Player 16",
    "Player 17",
    "Player 18",
    "Player 19",
    "Player 20",
    "Player 21",
    "Player 22",
    "Player 23",
    "Player 24",
    "Player 25",
    "Player 26",
    "Player 27",
    "Player 28",
    "Player 29",
    "Player 30",
    "Player 31",
    "Player 32",
    "Player 33",
    "Player 34",
    "Player 35",
    "Player 36"
];

function populateRacerNames(racerNames) {
    let datalist = document.getElementById("racerNames");
    for (let racerName of racerNames) {
        let option = document.createElement("option");
        option.value = racerName;
        datalist.appendChild(option);
    }
}

async function checkElimination(racerName) {
    const data = await network.post(`http://${BASE_IP}/check-elimination`, { "racer_name": racerName }, false);
    if (data) {
        if (data.eliminated == null) {
            showPopup("No racer was found with that name.\nPlease check your spelling and try again.", () => {}, true);
        } else if (data.eliminated === true) {
            showPopup("Sorry, but you have been eliminated. Better luck next time.", () => {}, true);
        } else if (data.eliminated === false) {
            showPopup("You're still in the running! You'll be up to race again soon.", () => {}, true);
        }
    }
}