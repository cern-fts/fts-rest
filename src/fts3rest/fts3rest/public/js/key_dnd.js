
function handleDragOver(event)
{
    event.stopPropagation();
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
}


function handleDrop(event)
{
    event.stopPropagation();
    event.preventDefault();

    var pkey_textbox = document.getElementById("private-key");

    var file = event.dataTransfer.files[0];
    var reader = new FileReader();

    reader.onloadend = function(event) {
        if (event.target.readyState == FileReader.DONE) {
            pkey_textbox.value = event.target.result;
        }
    };

    reader.readAsText(file);
}


if (window.File && window.FileReader) {
    var pkey_p = document.getElementById("private-key-paragraph");
    var dnd_notification = document.createElement("small");
    dnd_notification.innerHTML = "You can try to drag and drop your private key into the text area (if it is not password protected)"
    pkey_p.appendChild(dnd_notification);

    // Attach event listener
    var pkey_textbox = document.getElementById("private-key");
    pkey_textbox.addEventListener('dragover', handleDragOver, false);
    pkey_textbox.addEventListener('drop', handleDrop, false);
}