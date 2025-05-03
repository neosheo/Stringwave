var original_bg_color;
var track_data;

document.querySelector("table").addEventListener("click", (event) => {
    // only update button variable if user clicked the edit button
    if (event.target.className === "edit-button-img") {
        const button = event.target.closest(".edit-button");
        // parent is a td with class "box"
        const buttonParent = button.parentElement;
        // get the elements containing the track's title and artist so they can be edited
        const track_title = buttonParent.nextElementSibling.nextElementSibling.querySelector(".track-title");
        const track_artist = buttonParent.nextElementSibling.nextElementSibling.nextElementSibling.querySelector(".track-title");
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
        const new_button = document.createElement("button");
        new_button.className = "done-button button linea-icon";
        new_button.type = "submit";
        const button_img = document.createElement("img");
        button_img.src = "/static/images/basic_elaboration_bookmark_check.svg";
        button_img.alt = "Done";
        button_img.setAttribute("height", "20");
        button_img.setAttribute("width", "20");
        button_img.className = "done-button-img";
        new_button.appendChild(button_img);
        button.replaceWith(new_button);
    // only update button variable if user clicked the done button
    } else if (event.target.className === "done-button-img") {
        const button = event.target.closest(".done-button");
        const buttonParent = button.parentElement;
        const track_title = buttonParent.nextElementSibling.nextElementSibling.querySelector(".track-title");
        const track_artist = buttonParent.nextElementSibling.nextElementSibling.nextElementSibling.querySelector(".track-title");
        const track_id = track_title.parentElement.querySelector(".track-id").innerHTML;
        const url = window.location.href.split("/");
        const station = url[url.length - 1];
        for (let key in track_data) {
            track_data[key].contentEditable = false;
            track_data[key].style.backgroundColor = original_bg_color;
        };
        // update track data with updated data
        track_data["title"] = track_title.textContent;
        track_data["artist"] = track_artist.textContent;
        // replace done button with edit button
        const old_button = document.createElement("button");
        old_button.className = "edit-button button linea-icon";
        old_button.type = "submit";
        const button_img = document.createElement("img");
        button_img.src = "/static/images/software_pencil.svg";
        button_img.alt = "Edit";
        button_img.className = "edit-button-img";
        button_img.setAttribute("height", "20");
        button_img.setAttribute("width", "20");
        old_button.appendChild(button_img);
        button.replaceWith(old_button);
        // set new track data to update button
        const update_button = old_button.parentElement.querySelector(".update-button");
        update_button.setAttribute("value", `${track_id};${track_data["title"]};${track_data["artist"]};${station}`);
        }
    }
);
