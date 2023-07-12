async function nowPlaying() {
    const response = await fetch('/static/now_playing');
    const data = await response.text();
    console.log(data);
    if (data !== "") {
		const track = document.createElement("h1");
		track.id = "now_playing";
		const node = document.createTextNode(data);
		track.appendChild(node);
		const element = document.getElementById("now_playing");
		element.replaceWith(para);
	}
	setTimeout(nowPlaying, 5000);
}

nowPlaying();