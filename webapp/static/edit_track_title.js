const table_a = document.querySelector("table");

table_a.addEventListener("click", function(event) {
  if (event.target.closest(".edit-button")) {
    let button = event.target.closest(".edit-button");
    let track_title = button.parentElement.querySelector(".track-title");
    let new_button = document.createElement("button");
    new_button.id = "update-title";
    new_button.className = "done-button button linea-icon";
    new_button.type = "submit";
    new_button.form = "update-title";
    new_button.name = "update-title";
    new_button.value = "";
    new_button.innerHTML = '<img src="/static/images/basic_elaboration_bookmark_check.svg" alt="Done" height="20" width="20">';
    button.replaceWith(new_button);
    track_title.contentEditable = true;
    track_title.style.backgroundColor = "#e95959ad";
    track_title.style.width = "500px";
  }
  if (event.target.closest(".done-button")) {
    let button = event.target.closest(".done-button");
    let track_title = button.parentElement.querySelector(".track-title");
    track_title.contentEditable = false;
    track_title.style.backgroundColor = "#99001a";
    let url = window.location.href.split("/");
    let station = url[url.length - 1];
    box = event.target.closest("td");
    let track_id = box.querySelector(".track-id").innerHTML;
    let new_title = box.querySelector(".track-title").innerHTML;
    let update_button = button.parentElement.querySelector(".update-button");
    update_button.setAttribute("value", `${track_id};${new_title};${station}`);
    //console.log(`${track_id};${new_title};${station}`);
    let old_button = document.createElement("button");
    old_button.className = "edit-button button linea-icon";
    old_button.type = "submit";
    old_button.innerHTML = '<img src="/static/images/software_pencil.svg" alt="Edit" height="20" width="20">';
    button.replaceWith(old_button);
  }
});
