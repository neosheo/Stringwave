async function checkMoveStatus() {
    const response = await fetch('/move_status');
    const data = await response.text();
    const json_data = JSON.parse(data);
    if (json_data['status'] === 'complete') {
        window.location.replace('/tracks_new');
    }
    setTimeout(checkMoveStatus, 5000);
}

checkMoveStatus();