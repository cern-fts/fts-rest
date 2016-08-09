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

var template_server_status = null;

/**
 * Tell the server to set hostname to drain
 */
function setServerDrain(hostname, drain)
{
    $.ajax({
        url: "/config/drain",
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({hostname: hostname, drain: drain})
    })
    .done(function(data, textStatus, jqXHR) {
        refreshOverview();
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}

/**
 * Compile templates embedded into the HTML
 */
function compileTemplates()
{
    template_server_status = Handlebars.compile(
        $("#server-status-template").html()
    );
}

/**
 * Refresh the overview
 */
function refreshOverview()
{
    var tbody = $("#server-statuses");

    $.ajax({
     		headers: {          
                 Accept : "application/json",
            },
        	url: "/config?",
        	success: function (data) {
            // Decorate each entry with its state
            $.each(data, function(i, server) {
            	var beat = server.beat;
            	beat = beat.concat('Z');
            	var ms = 2 * 60 * 1000;
                if (server.drain) {
                    server.status_klass = 'btn-warning';
                    server.status_lbl = 'Draining';
                    server.is_draining = true;
                }
                else if (new Date(beat) < (new Date().getTime() - ms)) {
                    server.status_klass = 'btn-danger';
                    server.status_lbl = 'Offline';
                    server.is_draining = false;
                }
                else {
                    server.status_klass = 'btn-success';
                    server.status_lbl = 'Ok';
                    server.is_draining = true;
                }
            });

            tbody.empty();
            var trs = $(template_server_status(data));
            tbody.append(trs);
        }
    });
}

/**
 * Setup the overview view
 */
function setupOverview()
{
    compileTemplates();
    refreshOverview();
}
