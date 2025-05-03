let originalBGColor;

document.querySelector("table").addEventListener("click", (event) => {
    // only update button variable if user clicked the edit button
    if (event.target.className === "edit-button-img") {
        const button = event.target.closest(".edit-button");
        // parent is a td with class "box"
        const buttonParent = button.parentElement;

        // extract title and artist elements
        const trackTitleElement = buttonParent.nextElementSibling.nextElementSibling.querySelector(".track-title");
        const trackArtistElement = buttonParent.nextElementSibling.nextElementSibling.nextElementSibling.querySelector(".track-title");
        const editableElements = [trackTitleElement, trackArtistElement];

        // the background color is actually stored in the element 2 parents above button
        originalBGColor = window.getComputedStyle(buttonParent.parentElement).backgroundColor;

        // make each element editable
        for (let elem of editableElements) {
            elem.contentEditable = true;
            elem.style.backgroundColor = "#e95959ad";
        }

        // replace edit button with done button
        const newButton = document.createElement("button");
        newButton.className = "done-button button linea-icon";
        newButton.type = "submit";
        const buttonImage = document.createElement("img");
        buttonImage.src = "/static/images/basic_floppydisk.svg";
        buttonImage.alt = "Done";
        buttonImage.setAttribute("height", "30");
        buttonImage.setAttribute("width", "30");
        buttonImage.className = "done-button-img";
        newButton.appendChild(buttonImage);
        button.replaceWith(newButton);

    // only update button variable if user clicked the done button
    } else if (event.target.className === "done-button-img") {
        const button = event.target.closest(".done-button");
        const buttonParent = button.parentElement;

        const trackTitleElement = buttonParent.nextElementSibling.nextElementSibling.querySelector(".track-title");
        const trackArtistElement = buttonParent.nextElementSibling.nextElementSibling.nextElementSibling.querySelector(".track-title");
        const editableElements = [trackTitleElement, trackArtistElement];
        const trackId = trackTitleElement.parentElement.querySelector(".track-id").innerHTML;

        // get station
        const url = window.location.href.split("/");
        const station = url[url.length - 1];

        // create an object with the track data
        const trackData = {
            track_id: trackId,
            title: trackTitleElement.textContent,
            artist: trackArtistElement.textContent,
            station: station
        };

        // remove editable text boxes
        for (let elem of editableElements) {
            elem.contentEditable = false;
            elem.style.backgroundColor = originalBGColor;
        };

        fetch("/update_track_data",
        {
            headers: {
				"Accept": "application/json",
				"Content-Type": "application/json"
            },
            method: "POST",
            body: JSON.stringify(trackData)
        });

        // replace done button with edit button
        const oldButton = document.createElement("button");
        oldButton.className = "edit-button button linea-icon";
        oldButton.type = "submit";
        const buttonImage = document.createElement("img");
        buttonImage.src = "/static/images/software_pencil.svg";
        buttonImage.alt = "Edit";
        buttonImage.className = "edit-button-img";
        buttonImage.setAttribute("height", "30");
        buttonImage.setAttribute("width", "30");
        oldButton.appendChild(buttonImage);
        button.replaceWith(oldButton);
        }
    }
);
