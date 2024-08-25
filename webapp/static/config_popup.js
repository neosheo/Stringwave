document.addEventListener("DOMContentLoaded", () => {
    // Select all elements with the .config-hover class
    let configHoverElems = document.querySelectorAll('.config-hover');

    // Loop through each config-hover element
    configHoverElems.forEach((elem) => {
        elem.addEventListener('mousemove', (event) => {
            // Get mouse cursor position
            let mouseX = event.clientX;
            let mouseY = event.clientY;

            // Get the info box associated with this config-hover element
            let infoBox = this.querySelector('.info');

            // Show the info box
            infoBox.style.display = 'block';

            // Position the info box relative to the cursor
            infoBox.style.top = mouseY + 'px';
            infoBox.style.left = mouseX + 'px';
        });

        elem.addEventListener('mouseleave', () => {
            // Get the info box associated with this config-hover element
            let infoBox = this.querySelector('.info');

            // Hide the info box when mouse leaves the element
            infoBox.style.display = 'none';
        });
    });
});
