function showAlertPopup() {
    showPopup(
        "Are you sure you want to alert the controller?<br>This will likely stop event flow.",
        async function () { 
            await network.post(`http://${BASE_IP}/alert-controller`); 
        }
    );
}

setInterval(async () => {
    const data = await network.get(`http://${BASE_IP}/check-emcee-alert`);

    if (data && data["message"]) {
        showPopup(`You have an incoming alert from the controller.\nThe controller says:\n\n${data["message"]}`, () => {}, true);
        await network.post(`http://${BASE_IP}/clear-emcee-alert`)
    }
}, 1000)