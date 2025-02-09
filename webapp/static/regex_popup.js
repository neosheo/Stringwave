document.getElementById("artist-list").addEventListener("click", (event) => {
    if (event.target.className === "regex-button-img") {
        const regexButton = event.target.parentElement;
        // get the channel id from the refresh icon button next to it
        // get the channel name from the title above
        // const channel_id = regexButton.previousElementSibling.value;
        const channel_name = regexButton.parentElement.querySelector(".channel-name").innerHTML;
        // show regex popup
        const regexPopup = regexButton.parentElement.querySelector(".regex-popup");
        regexPopup.style.visibility = "visible";
        const regexHeader = regexPopup.querySelector(".regex-header");
        regexHeader.innerHTML = `Edit Regex Pattern for ${channel_name}`;
        const regexPattern = regexPopup.querySelector(".regex-pattern");
        regexPattern.contentEditable = true;
        regexPattern.style.width = "70%";
        regexPattern.style.backgroundColor = "#e95959ad";
        
    } else if (event.target.className === "save-regex-button-img") {
        const regexPopup = event.target.parentElement.parentElement.parentElement;
        const channel_id = regexPopup.querySelector(".save-regex-button").value;
        const regexPattern = regexPopup.querySelector(".regex-pattern").textContent;
        const regexType = regexPopup.querySelector('input[name="regex-type"]:checked').value;
		const regexData = {
			channel_id: channel_id,
			video_title_regex: regexPattern,
			regex_type: regexType
		};
		fetch("/add_regex",
		{
			headers: {
				"Accept": "application/json",
				"Content-Type": "application/json"
			},
			method: "POST",
			body: JSON.stringify(regexData)
		});
			
        /* const regexData = `${channel_id};${regexPattern};${regexType}`; */
        // assign regex data to the form
        /* document.getElementById("regex-data").value = regexData; */
        // submit the form
        /* document.getElementById("add-regex").submit(); */
        // hide the regex popup
        regexPopup.style.visibility = "hidden";
    } else if (event.target.className === "close-regex-button-img") {
        // hide regex popup
        const regexPopup = event.target.parentElement.parentElement.parentElement;
        regexPopup.style.visibility = "hidden";
    }
})
