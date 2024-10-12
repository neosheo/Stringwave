document.getElementById("artist-list").addEventListener("click", (event) => {
  if (event.target.closest(".edit-button")) {
    let button = event.target.closest(".edit-button");
    // parent element is a div with class "title"
    // select the class "artist" within the div
    let artist = button.parentElement.querySelector(".artist");
    // make done button
    let new_button = document.createElement("button");
    new_button.className = "done-button button linea-icon small-icon";
    new_button.type = "submit";
    // add image to button
    let button_img = document.createElement("img");
    button_img.src = "/static/images/basic_elaboration_bookmark_check.svg";
    button_img.alt = "Done";
    button_img.className = "done-button-img";
    new_button.appendChild(button_img);
    // new_button.innerHTML = '<img src="/static/images/basic_elaboration_bookmark_check.svg" alt="Done" height="20" width="20">';
    button.replaceWith(new_button);
    // make subscription name editable
    artist.contentEditable = true;
    artist.style.color = "black;"
    artist.style.backgroundColor = "#e95959ad";
  }

  if (event.target.closest(".done-button")) {
    let button = event.target.closest(".done-button");
    let artist = button.parentElement.querySelector(".artist");
    // make edit button
    let old_button = document.createElement("button");
    old_button.type = "submit";
    // add image to button
    let button_img = document.createElement("img");
    button_img.src = "/static/images/software_pencil.svg";
    button_img.alt = "Edit";
    button_img.className = "edit-button-img";
    old_button.appendChild(button_img);
    old_button.className = "edit-button button linea-icon small-icon";
    // old_button.innerHTML = '<img src="/static/images/software_pencil.svg" alt="Edit" height="20" width="20">'
    button.replaceWith(old_button);
    // make subscription name not editable
    artist.contentEditable = false;
    // add new artist information to the update button
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
