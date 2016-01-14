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
 * Updates the list of configured groups
 */
function refreshGroupList()
{
	var tbody = $("#group-list");

    $.ajax({
        url: "/config/groups?",
        contentType: "application/json"
    })
    .done(function(data, textStatus, jqXHR) {
        tbody.empty();

        $.each(data, function(i, member) {
            var tr = $("<tr></tr>");

            var deleteBtn = $("<button class='btn btn-link'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i>");

            deleteBtn.click(function() {
                tr.css("background", "#d9534f");
                $.ajax({
                    url: "/config/groups/" + encodeURIComponent(member.groupname) + "?member=" + encodeURIComponent(member.member),
                    type: "DELETE",
                    contentType: "application/json"
                })
                .done(function(data, textStatus, jqXHR) {
                    tr.fadeOut(300, function() {tr.remove();})
                })
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                    tr.css("background", "#ffffff");
                });
            });

            tr.append($("<td></td>").append(deleteBtn))
              .append($("<td></td>").text(member.groupname))
              .append($("<td></td>").text(member.member));
            tbody.append(tr);
        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}


/**
 * Initializes the group view
 */
function setupGroups()
{
	// Refresh
	refreshGroupList();

    // Attach to forms
    $("#group-add-frm").submit(function(event) {
        $.ajax({
            url: "/config/groups",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: $(this).serialize()
        })
        .done(function(data, textStatus, jqXHR) {
            refreshGroupList();
            $("#group-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
        .always(function() {
            $("#group-add-frm input").prop("disabled", false);
            $("#group-add-frm input> i").attr("class", "glyphicon glyphicon-plus");
        });

        $("#group-add-frm input").prop("disabled", true);
        $("#group-add-frm input>i").attr("class", "glyphicon glyphicon-refresh");

        event.preventDefault();
    });

	// Autocomplete
	$("#group-add-field-member").autocomplete({
		source: "/autocomplete/storage"
	});
	$("#group-add-field-groupname").autocomplete({
		source: "/autocomplete/groupname"
	});
}
