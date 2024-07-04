document.getElementById("artist-list").addEventListener("click", (event) => {
  if (event.target.closest(".edit-button")) {
    let button = event.target.closest(".edit-button");
    let artist = button.parentElement.querySelector(".artist");
    let new_button = document.createElement("button");
    new_button.className = "done-button button linea-icon";
    new_button.type = "submit";
    new_button.innerHTML = '<img src="/static/images/basic_elaboration_bookmark_check.svg" alt="Done" height="20" width="20">';
    button.replaceWith(new_button);
    artist.contentEditable = true;
    artist.style.color = "black;"
    artist.style.backgroundColor = "#e95959ad";
  }
  if (event.target.closest(".done-button")) {
    let button = event.target.closest(".done-button");
    let artist = button.parentElement.querySelector(".artist");
    let old_button = document.createElement("button");
    old_button.className = "edit-button button linea-icon";
    old_button.type = "submit";
    old_button.innerHTML = '<img src="/static/images/software_pencil.svg" alt="Edit" height="20" width="20">'
    button.replaceWith(old_button);
    artist.contentEditable = false;
    let url;
    let box;
    let channel_id;
    let new_artist;
    let update_button = old_button.parentElement.querySelector(".update-button");
    channel_id = update_button.parentElement.children[4].children[0].innerHTML;
    artist.style.backgroundColor = "black";
    new_artist = update_button.parentElement.querySelector(".artist").innerHTML;
    update_button.setAttribute("value", `${channel_id};${new_artist}`);
    }
  }
);
