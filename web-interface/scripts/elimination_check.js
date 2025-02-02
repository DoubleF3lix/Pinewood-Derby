const racerNames = [
    
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