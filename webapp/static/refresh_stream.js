const url = window.location.href.split("/");
const station = url[url.length - 1];
let audioElement = document.getElementById("audio-controls");
let source = document.getElementById("stream");
/* the counter variable prevents the play event
listener from running when pressing the play button
for the first time and prevents an infinite play
loop after pressing play button subsequent times */
let counter = 0;

audioElement.addEventListener("pause", function() {
    audioElement.pause();
    source.removeAttribute('src');

});

audioElement.addEventListener("play", function() {
    if (counter === 0) {
        counter++;
    } else {
        source.setAttribute('src', `/${station}`);
        audioElement.load();
        counter--;
        audioElement.play();
    }
});