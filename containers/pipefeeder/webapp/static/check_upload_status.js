async function checkUploadStatus() {
    const response = await fetch('upload_status');
    const data = await response.text();
    if (data === 'complete') {
        window.location.replace('/list_subs');
    }
    setTimeout(checkUploadStatus, 5000);
}

checkUploadStatus();