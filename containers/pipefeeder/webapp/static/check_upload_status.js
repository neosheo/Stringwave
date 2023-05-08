async function checkUploadStatus() {
    let myloc = window.location.href;
    let locarray = myloc.split('/');
    delete locarray[(locarray.length - 1)];
    let arraytext = locarray.join('/');
    console.log(arraytext);
    const response = await fetch('.upload');
    const data = await response.text();
    if (data === 'complete') {
        window.location.replace('/list_subs');
    }
    setTimeout(checkUploadStatus, 5000);
}

checkUploadStatus();