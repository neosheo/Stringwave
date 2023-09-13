async function nowPlaying() {
	const url = window.location.href.split("/");
	const station = url[url.length - 1];
    const response = await fetch(`/static/now_playing_${station}`);
    const data = await response.text();
    // console.log(data);
    if (data !== "") {
		const track = document.createElement("h1");
		track.id = "now_playing";
		const node = document.createTextNode(data);
		track.appendChild(node);
		const element = document.getElementById("now_playing");
		element.replaceWith(track);
		document.title = track.innerHTML;
	}
	setTimeout(nowPlaying, 5000);
}

nowPlaying();
