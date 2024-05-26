// grab appropriate element depending on which page you are on
let table_b;
if (document.getElementById("tracks-table") !== null) {
  table_b = document.querySelector("table");
} else {
  table_b = document.getElementById("artist-list");
}

table_b.addEventListener("click", (event) => {
  if (event.target.closest(".edit-button")) {
    let button = event.target.closest(".edit-button");
    let track_artist = button.parentElement.querySelector(".track-artist");
    let new_button = document.createElement("button");
    new_button.className = "done-button button linea-icon";
    new_button.type = "submit";
    new_button.innerHTML = '<img src="/static/images/basic_elaboration_bookmark_check.svg" alt="Done" height="20" width="20">';
    button.replaceWith(new_button);
    track_artist.contentEditable = true;
    track_artist.style.color = "black;"
    track_artist.style.backgroundColor = "#e95959ad";
    track_artist.style.width = "500px";
    track_artist.style.margin = "auto";
  }
  if (event.target.closest(".done-button")) {
    let button = event.target.closest(".done-button");
    let track_artist = button.parentElement.querySelector(".track-artist");
    let old_button = document.createElement("button");
    old_button.className = "edit-button button linea-icon";
    old_button.type = "submit";
    old_button.innerHTML = '<img src="/static/images/software_pencil.svg" alt="Edit" height="20" width="20">'
    button.replaceWith(old_button);
    track_artist.contentEditable = false;
    let url;
    let station;
    let box;
    let track_id;
    let new_artist;
    let update_button = old_button.parentElement.querySelector(".update-button");
    if (window.location.href.includes("/tracks/")) {
      url = window.location.href.split("/");
      station = url[url.length - 1];
      box = event.target.closest("td");
      track_id = box.querySelector(".track-id").innerHTML;
      new_artist = box.querySelector(".track-artist").innerHTML;
      track_artist.style.backgroundColor = "#c93920";
    } else {
      station = "0"
      track_id = update_button.parentElement.children[3].children[0].innerHTML;
      track_artist.style.backgroundColor = "black";
    }
    new_artist = update_button.parentElement.querySelector(".track-artist").innerHTML;
    update_button.setAttribute("value", `${track_id};${new_artist};${station}`);
    //console.log(`${track_id};${new_artist};${station}`);
    }
  }
);
