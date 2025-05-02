const trackQueue = [];

document.querySelector("table").addEventListener("click", (event) => {
    if (event.target.className === "queue-button-img") {
        let button = event.target.closest(".queue-button");
        let trackRow = button.closest(".track-row");
        let trackId = trackRow.querySelector(".track-id").innerText;
        // add track id to queue
        trackQueue.push(trackId);
        // make queue buttons visible if an item is added to the queue and they are hidden
        // there should only be one element with this class
        const queueContainer = document.getElementsByClassName("queue-container")[0];
        if (trackQueue.length > 0 && (queueContainer.style.visibility === "hidden" || queueContainer.style.visibility === "")) {
            queueContainer.style.visibility = "visible";
        } 
    }
})

