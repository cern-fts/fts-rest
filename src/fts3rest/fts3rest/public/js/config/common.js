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


/**
 * Display an error
 */
function errorMessage(jqXHR)
{
    var msg;
    if (jqXHR.responseJSON && jqXHR.responseJSON.message)
        msg = jqXHR.responseJSON.message;
    else
        msg = "The server didn't return an error message: " + jqXHR.textStatus;

    $("#err-dialog-msg").text(msg);
    $("#err-dialog").modal('show');
}

/**
 * Bind the 'enter key' press to func for every input field inside form
 */
function bindMethodToEnterOnInput(form, func)
{
    form.find("input").keydown(function(event) {
        if (event.which == 13) {
            event.preventDefault();
            func(event);
            return false;
        }
        return true;
    });
}

/**
 * Helper for select elements
 */
Handlebars.registerHelper('selected', function(option, value){
    if (option === value) {
        return ' selected';
    } else {
        return ''
    }
});
