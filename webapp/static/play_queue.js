// this makes station accessible to other scripts that may need it in the future
const url = window.location.href.split("/");
const station = url[url.length - 1];
    
// if user presses queue and play button make sure play_now is set to 1
document.getElementById("queue-play-now-button").addEventListener("click", (event) => {
    addTracksToQueue("1");
});

// if user presses queue button make sure play_now is set to 0
document.getElementById("queue-button").addEventListener("click", (event) => {
    addTracksToQueue("0");
});


function addTracksToQueue(playNow) {
    // submit queue to webapp
    fetch(`/queue/${playNow}/${station}`,
		{
            headers: {
              "Accept": "application/json",
               "Content-Type": "application/json"
            },
			method: "POST",
			body: JSON.stringify(trackQueue)
        }
    );

    // clear queue
    trackQueue.length = 0;
}