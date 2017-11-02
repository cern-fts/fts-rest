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
 * Queries from the server the list of authorized dns and
 * refresh the display
 */
function refreshAuthzList()
{
    var tbody = $("#authz-list");

    $.ajax({
        headers: {
            Accept : "application/json",
        },
        url: "/config/authorize?",
    })
    .done(function (data) {
        tbody.empty();
        $.each(data, function(i, user) {
            var tr = $("<tr></tr>");

            var deleteBtn = $("<button class='btn btn-link' type='button' id='button-delete-authz'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i>");

            deleteBtn.click(function() {
                tr.css("background", "#d9534f");
                $.ajax({
                    url: "/config/authorize?dn=" + encodeURIComponent(user.dn) + "&operation=" + encodeURIComponent(user.operation),
                    contentType: "application/json",
                    type: "DELETE"
                })
                .done(function(data, textStatus, jqXHR) {
                    tr.fadeOut(300, function() {tr.remove();})
                })
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                    tr.css("background", "#ffffff");
                });
            });

            tbody.append(
                tr.append($("<td></td>").append(deleteBtn))
                  .append($("<td></td>").append($("<span class='monospace'></span>").text(user.dn)))
                  .append($("<td></td>").text(user.operation))
            );
        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}
(function ($) {
    $.fn.serializeFormJSON = function () {

        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };
})(jQuery);
/**
 * Initialize the authz view
 */
function setupAuthz()
{
    // Load list
    refreshAuthzList();
   

    // Attach to the form
    $("#authz-add-frm").submit(function(event) {
        var data = $(this).serialize().split("&");
   		console.log(data);
    	var obj={};
    	for(var key in data)
    	{
        	console.log(data[key]);
        	
        	obj[data[key].split("=")[0]] = decodeURIComponent((data[key].split("=")[1]).replace(/\+/g, ' '));
    	}
        $.ajax({
            url: "/config/authorize?",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(obj)
        })
        .done(function(data, textStatus, jqXHR) {
            refreshAuthzList();
            $("#authz-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
        .always(function() {
            $("#auth-add-frm-submit > i").attr("class", "glyphicon glyphicon-plus");
        });

        $("#auth-add-frm-submit > i").attr("class", "glyphicon glyphicon-refresh");

        event.preventDefault();
    });

    // Autocomplete
    $("#authz-add-field-dn").autocomplete({
        source: "/autocomplete/dn"
    });
}
