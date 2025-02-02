const BASE_IP = "192.168.132.106:3000";


let shouldUpdateData = true;

function startGetRaceInfoLoop() {
    setInterval(async () => {
        if (shouldUpdateData === true) {
            const data = await network.get(`http://${BASE_IP}/get-race-info`);
            console.log(data);

            document.getElementById("racer_now").textContent = "Now Racing: " + data["now"][0] + " vs. " + data["now"][1];
            document.getElementById("racer_next").textContent = "Up Next: " + data["next"][0] + " vs. " + data["next"][1];
            document.getElementById("races_left_in_round").textContent = "Races Left in Round: " + data["races_left_in_round"];
            document.getElementById("players_left").textContent = "Players Left: " + data["players_left"];
        }
    }, 1000)
}

const network = {
    async post(url, data, silent = false) {
        let response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        try {
            if (!silent) {
                console.log(`Sending POST request to ${url} with data ${JSON.stringify(data)} - response: ${response.status}`);
            }
            return await response.json();
        } catch {
            // console.log(`No JSON to return from request, response code ${response.status}`);
        }
    },
    async get(url, silent = true) {
        let response = await fetch(url);
        try {
            if (!silent) {
                console.log(`Sending GET request to ${url} - response: ${response.status}`);
            }
            return await response.json();
        } catch {
            // console.log(`No JSON to return from request, response code ${response.status}`);
        }
    }
};

function makePopup() {
    // Popup Background
    const popupBackgroundDiv = document.createElement("div");
    popupBackgroundDiv.id = "popupBackground";
    document.body.appendChild(popupBackgroundDiv);

    // Popup Main
    const popupMainDiv = document.createElement("div");
    popupMainDiv.id = "popupMain";

    // Popup exit button (X in the corner)
    const popupExitButton = document.createElement("button");
    popupExitButton.id = "popupExitButton";
    popupExitButton.textContent = "\u2716"; // ✖ / &#10006;
    popupExitButton.onclick = hidePopup; // Should be overwritten by the user in the definition
    popupMainDiv.appendChild(popupExitButton);

    // Popup text
    const popupText = document.createElement("p");
    popupText.id = "popupText";
    popupText.textContent = "You shouldn't be seeing this";
    popupMainDiv.appendChild(popupText);

    // Popup buttons
    const popupButtonContainer = document.createElement("div");
    popupButtonContainer.id = "popupButtonContainer";

    // Confirm button
    const popupConfirmButton = document.createElement("button");
    popupConfirmButton.id = "popupConfirmButton";
    popupConfirmButton.textContent = "Confirm";
    popupConfirmButton.onclick = hidePopup; // Should be overwritten by the user in the definition
    popupConfirmButton.classList.add("standardButton", "greenButton", "inline")

    // Cancel button
    const popupCancelButton = document.createElement("button");
    popupCancelButton.id = "popupCancelButton";
    popupCancelButton.textContent = "Cancel";
    popupCancelButton.onclick = hidePopup;
    popupCancelButton.classList.add("standardButton", "redButton", "inline", "nonLeftButtonSpacer");


    // Adding buttons to the container
    popupButtonContainer.appendChild(popupConfirmButton);
    popupButtonContainer.appendChild(popupCancelButton);

    // Adding the container to the main DIV
    popupMainDiv.appendChild(popupButtonContainer);

    // Adding the main DIV to the body
    document.body.appendChild(popupMainDiv);
}

function showPopup(popupTextContent, onConfirm = () => { }, hideCancel = false) {
    document.getElementById("popupText").innerHTML = popupTextContent.replace(/\n/g, "<br>");
    document.getElementById("popupConfirmButton").onclick = function () {
        onConfirm();
        hidePopup();
    };
    // Swap out the buttons if we should hide the cancel button
    if (hideCancel === true) {
        document.getElementById("popupConfirmButton").textContent = "OK";
        document.getElementById("popupCancelButton").style.display = "none";
    }
    document.getElementById("popupBackground").style.visibility = "visible";
    document.getElementById("popupMain").style.visibility = "visible";
    shouldUpdateData = false;
}

function hidePopup() {
    document.getElementById("popupBackground").style.visibility = "hidden";
    document.getElementById("popupMain").style.visibility = "hidden";
    shouldUpdateData = true;

    // Put the old popup stuff back in case it was shown without the Cancel button
    document.getElementById("popupConfirmButton").textContent = "Confirm";
    document.getElementById("popupCancelButton").style.display = "inline-block";
}