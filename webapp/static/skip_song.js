function skipSong() {
    const url = window.location.href.split("/");
	const station = url[url.length - 1];
    fetch(`/skip/${station}`);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('skip')
    .addEventListener('click', skipSong);
});