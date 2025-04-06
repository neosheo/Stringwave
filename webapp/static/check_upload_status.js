async function checkUploadStatus() {
    const response = await fetch('/pipefeeder/upload_status');
    const data = await response.text();
    const json_data = JSON.parse(data);
    if (json_data['status'] === 'complete') {
        window.location.replace('/pipefeeder/list_subs');
    }
    setTimeout(checkUploadStatus, 5000);
}

checkUploadStatus();