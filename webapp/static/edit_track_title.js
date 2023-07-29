const table = document.querySelector("table");

table.addEventListener("click", function(event) {
  if (event.target.closest(".edit-button")) {
    const button = event.target.closest(".edit-button");
    const track_title = button.parentElement.querySelector(".track-title");
    track_title.contentEditable = true;
    track_title.style.backgroundColor = "#dddbdb";
  }
  if (event.target.closest(".done-button")) {
    const button = event.target.closest(".done-button");
    const track_title = button.parentElement.querySelector(".track-title");
    track_title.contentEditable = false;
    track_title.style.backgroundColor = "#c93920";
    const url = window.location.href.split("/");
	const station = url[url.length - 1];
    box = event.target.closest("td");
    let track_id = box.querySelector(".track-id").innerHTML;
    let new_title = box.querySelector(".track-title").innerHTML;
    const update_button = button.parentElement.querySelector(".update-button");
    update_button.setAttribute("value", `${track_id};${new_title};${station}`);
    console.log(`${track_id};${new_title};${station}`);
  }
});
