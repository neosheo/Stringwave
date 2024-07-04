var original_bg_color;
var track_data;

document.querySelector("table").addEventListener("click", (event) => {
    // only update button variable if user clicked the edit button
    if (event.target.className === "edit-button-img") {
        let button = event.target.closest(".edit-button");
        let buttonParent = event.target.closest(".edit-button").parentElement;
        let track_title = buttonParent.nextElementSibling.querySelector(".track-title");
        let track_artist = buttonParent.nextElementSibling.nextElementSibling.querySelector(".track-title");
        track_data = {
            artist: track_artist,
            title: track_title
        };
        // the background color is actually stored in the element 2 parents above button
        original_bg_color = window.getComputedStyle(buttonParent.parentElement).backgroundColor;
        // make each key of track_data editable
        for (let key in track_data) {
            track_data[key].contentEditable = true;
            track_data[key].style.backgroundColor = "#e95959ad";
        }
        // replace edit button with done button
        let new_button = document.createElement("button");
        new_button.className = "done-button button linea-icon";
        new_button.type = "submit";
        new_button.innerHTML = '<img class="done-button-img" src="/static/images/basic_elaboration_bookmark_check.svg" alt="Done" height="20" width="20">';
        button.replaceWith(new_button);
    // only update button variable if user clicked the done button
    } else if (event.target.className === "done-button-img") {
        let button = event.target.closest(".done-button");
        let buttonParent = button.parentElement;
        let track_title = buttonParent.nextElementSibling.querySelector(".track-title");
        let track_artist = buttonParent.nextElementSibling.nextElementSibling.querySelector(".track-title");
        let track_id = track_title.parentElement.querySelector(".track-id").innerHTML;
        let url = window.location.href.split("/");
        let station = url[url.length - 1];
        for (let key in track_data) {
            track_data[key].contentEditable = false;
            track_data[key].style.backgroundColor = original_bg_color;
        };
        // update track data with updated data
        track_data["title"] = track_title.innerHTML;
        track_data["artist"] = track_artist.innerHTML;
        // replace done button with edit button
        let old_button = document.createElement("button");
        old_button.className = "edit-button button linea-icon";
        old_button.type = "submit";
        old_button.innerHTML = '<img class="edit-button-img" src="/static/images/software_pencil.svg" alt="Edit" height="20" width="20">'
        button.replaceWith(old_button);
        // set new track data to update button
        let update_button = old_button.parentElement.querySelector(".update-button");
        update_button.setAttribute("value", `${track_id};${track_data["title"]};${track_data["artist"]};${station}`);
        }
    }
);
