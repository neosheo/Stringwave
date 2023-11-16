async function skipSong() {
    const delay = ms => new Promise(res => setTimeout(res, ms));
    const audioElement = document.getElementById("audio-controls");
    const url = window.location.href.split("/");
	const station = url[url.length - 1];
    fetch(`/skip/${station}`);
    await delay(5000);
    audioElement.pause();
    audioElement.play();
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('skip')) {
        document.getElementById('skip')
        .addEventListener('click', skipSong);
    }
});
