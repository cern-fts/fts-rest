/*
 *  Copyright 2014 CERN
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
**/

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