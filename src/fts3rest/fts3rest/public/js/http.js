/*
 *  Copyright 2015 CERN
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

/** Just a small collection of utility functions */

function methodError()
{
    alert("Method failed");
}


function removeHtmlElement(elemId)
{
    return function () {
        if (this.status >= 400) {
            alert('Request failed (' + this.status.toString() + ')');
            return;
        }

        var domEnt = document.getElementById(elemId);
        domEnt.style.background = "#d9534f";
        domEnt.style.transition = "opacity 0.5s linear 0s";
        domEnt.style.opacity = 0;
        domEnt.addEventListener("transitionend", function() {
            domEnt.parentNode.removeChild(domEnt);
        });
    }
}


function httpDelete(url, htmlEntToRemove)
{
    var httpReq = new XMLHttpRequest();

    httpReq.addEventListener("error", methodError);
    httpReq.addEventListener("abort", methodError);
    httpReq.addEventListener("load", removeHtmlElement(htmlEntToRemove));
    httpReq.open("DELETE", url, true);
    httpReq.send();
}
