const table = document.querySelector("table");

table.addEventListener("click", function(event) {
  if (event.target.closest(".edit-button")) {
    const button = event.target.closest(".edit-button");
    const track_artist = button.parentElement.querySelector(".track-artist");
    const new_button = document.createElement("button");
    new_button.className = "done-button button linea-icon";
    new_button.type = "submit";
    new_button.innerHTML = '<img src="/static/images/basic_elaboration_bookmark_check.svg" alt="Done" height="20" width="20">';
    button.replaceWith(new_button);
    track_artist.contentEditable = true;
    track_artist.style.backgroundColor = "#dddbdb";
  }
  if (event.target.closest(".done-button")) {
    const button = event.target.closest(".done-button");
    const track_artist = button.parentElement.querySelector(".track-artist");
    const old_button = document.createElement("button");
    old_button.className = "edit-button button linea-icon";
    old_button.type = "submit";
    old_button.innerHTML = '<img src="/static/images/software_pencil.svg" alt="Edit" height="20" width="20">'
    button.replaceWith(old_button);
    track_artist.contentEditable = false;
    track_artist.style.backgroundColor = "#c93920";
    const url = window.location.href.split("/");
	  const station = url[url.length - 1];
    box = event.target.closest("td");
    let track_id = box.querySelector(".track-id").innerHTML;
    let new_artist = box.querySelector(".track-artist").innerHTML;
    const update_button = button.parentElement.querySelector(".update-button");
    update_button.setAttribute("value", `${track_id};${new_artist};${station}`);
    console.log(`${track_id};${new_artist};${station}`);
  }
});