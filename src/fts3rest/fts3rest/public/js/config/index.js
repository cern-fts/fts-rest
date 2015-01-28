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
 * Tell the server to set hostname to drain
 */
function setServerDrain(hostname, drain)
{
    $.post("/config/drain", {hostname: hostname, drain: drain})
    .done(function(data, textStatus, jqXHR) {
        setupOverview();
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}


/**
 * Setup the overview view
 */
function setupOverview()
{
    var tbody = $("#server-statuses");

    $.ajax({
        url: "/config?",
        success: function (data) {
            tbody.empty();
            $.each(data, function(i, server) {
                var status, klass;
                if (server.drain) {
                    klass = 'btn-warning';
                    status = 'Draining';
                }
                else if (new Date(server.beat) < (new Date().getTime() - (2 * 60 * 1000))) {
                    klass = 'btn-danger';
                    status = 'Offline';
                }
                else {
                    klass = 'btn-success';
                    status = 'Ok';
                }

                var btnGroup = $("<div class='btn-group'></div>");
                var btnStatus = $("<button></button>").text(status);
                btnStatus.append(" <span class='caret'></span>");
                btnStatus.addClass("btn btn-xs dropdown-toggle").addClass(klass);
                btnStatus.attr("data-toggle", "dropdown");

                btnGroup.append(btnStatus);

                var dropDown = $("<ul class='dropdown-menu' role='menu'>");

                var btnDrain;
                if (status != 'Draining') {
                    btnDrain = $("<li><a href='#'>Drain</a></li>");
                    btnDrain.click(function(e) {
                        btnStatus.prop("disabled", true); setServerDrain(server.hostname, true)
                    });
                }
                else {
                    btnDrain = $("<li><a href='#'>Undrain</a></li>");
                    btnDrain.click(function(e) {
                        btnStatus.prop("disabled", true); setServerDrain(server.hostname, false)
                    });
                }
                dropDown.append(btnDrain);

                btnGroup.append(dropDown);

                var tr = $("<tr></tr>")
                    .append($("<td></td>").text(server.hostname))
                    .append($("<td></td>").text(server.service_name))
                    .append($("<td></td>").text(server.beat).append(" ").append(btnGroup));
                tbody.append(tr);
            });
        }
    });
}
