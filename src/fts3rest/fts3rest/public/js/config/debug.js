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
 * Updates live the debug level
 */
function debugLevelSelect(debug)
{
	var select = $("<select class='form-control'></select>");
	$.each(["Verbose", "Very verbose", "Extremely verbose"], function(i, label) {
		var option = $("<option></option>")
			.text(label)
			.attr("value", i + 1);

		debug.debug_level = Math.min(1, debug.debug_level);
		debug.debug_level = Math.max(3, debug.debug_level);

		if (debug.debug_level == i + 1) {
			option.attr("selected", "selected");
		}

		select.append(option);
	});

	select.change(function(e) {
		var new_value = $(this).val();
		var select = $(this);
		select.prop("disabled", true);
		$.ajax({
			url: "/config/debug?",
			type: "POST",
			dataType: "json",
			data: {source_se: debug.source_se, dest_se: debug.dest_se, debug_level: new_value}
		})
		.fail(function(jqXHR) {
			errorMessage(jqXHR);
		})
		.always(function() {
			select.prop("disabled", false);
		});
	});

	return select;
}


/**
 * Updates the list of debug settings
 */
function refreshDebugList()
{
	var tbody = $("#debug-list");

    $.ajax({
        url: "/config/debug?"
    })
    .done(function (data) {
        tbody.empty();
        $.each(data, function(i, debug) {
    		var tr = $("<tr></tr>");

			var deleteBtn = $("<button class='btn btn-link'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i>");

            deleteBtn.click(function() {
                tr.css("background", "#d9534f");
                $.ajax({
                    url: "/config/debug?source_se=" + encodeURIComponent(debug.source_se) + "&dest_se=" + encodeURIComponent(debug.dest_se),
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
                  .append($("<td></td>").append($("<span class='monospace'></span>").text(debug.source_se)))
                  .append($("<td></td>").append($("<span class='monospace'></span>").text(debug.dest_se)))
                  .append($("<td></td>").append(debugLevelSelect(debug)))
            );
        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}

/**
 * Initializes the debug view
 */
function setupDebug()
{
	// Load list
	refreshDebugList();

	// Attach to the form
	$("#debug-add-frm").submit(function() {
        $.ajax({
            url: "/config/debug?",
            type: "POST",
            dataType: "json",
            data: $(this).serialize()
        })
        .done(function(data, textStatus, jqXHR) {
            refreshDebugList();
            $("#debug-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
        .always(function() {
            $("#debug-add-frm-submit > i").attr("class", "glyphicon glyphicon-plus");
        });

		$("#debug-add-frm-submit > i").attr("class", "glyphicon glyphicon-refresh");

		event.preventDefault();
	});

    // Autocomplete
    $("#debug-add-field-source").autocomplete({
        source: "/autocomplete/source"
    });
    $("#debug-add-field-destination").autocomplete({
        source: "/autocomplete/destination"
    });
}
