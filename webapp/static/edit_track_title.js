const table = document.querySelector("table");

table.addEventListener("click", function(event) {
  if (event.target.closest(".edit-button")) {
    const button = event.target.closest(".edit-button");
    const track_title = button.parentElement.querySelector(".track-title");
    const new_button = document.createElement("button");
    new_button.id = "update-title";
    new_button.className = "done-button button";
    new_button.type = "submit";
    new_button.form = "update-title";
    new_button.name = "update-title";
    new_button.value = "";
    new_button.innerHTML = "Done"
    button.replaceWith(new_button);
    track_title.contentEditable = true;
    track_title.style.backgroundColor = "#dddbdb";
  }
  if (event.target.closest(".done-button")) {
    const button = event.target.closest(".done-button");
    const track_title = button.parentElement.querySelector(".track-title");
    track_title.contentEditable = false;
    track_title.style.backgroundColor = "#99001a";
    const url = window.location.href.split("/");
	  const station = url[url.length - 1];
    box = event.target.closest("td");
    let track_id = box.querySelector(".track-id").innerHTML;
    let new_title = box.querySelector(".track-title").innerHTML;
    const update_button = button.parentElement.querySelector(".update-button");
    update_button.setAttribute("value", `${track_id};${new_title};${station}`);
    console.log(`${track_id};${new_title};${station}`);
    const old_button = document.createElement("button");
    old_button.className = "edit-button button";
    old_button.type = "submit";
    old_button.innerHTML = "Edit"
    button.replaceWith(old_button);
  }
});