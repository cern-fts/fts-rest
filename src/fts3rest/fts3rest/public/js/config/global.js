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
 * Updates the list of configured globals per VO
 */
function refreshVoConfigList()
{
	var tbody = $("#vo-config-list");

	$.ajax({
		url: "/config/global?",
		contentType: "application/json"
	})
	.done(function(data, textStatus, jqXHR) {
		tbody.empty();

		$.each(data, function(vo_name, vo) {
			if (vo_name && vo_name != "*") {
				var tr = $("<tr></tr>");

				var deleteBtn = $("<button class='btn btn-link'></button>")
	                .append("<i class='glyphicon glyphicon-trash'></i>");

	            deleteBtn.click(function() {
	                tr.css("background", "#d9534f");
	                $.ajax({
	                    url: "/config/global?vo_name=" + encodeURIComponent(vo_name),
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

	            var retryForm = $("<input type='number' min='0' max='10' class='form-control'></input>")
	            	.attr("value", vo.retry).
	            	change(function() {
	            		var retryInput = $(this);
	            		retryInput.prop("disabled", true);
	            		$.ajax({
	            			url: "/config/global?",
	            			type: "POST",
	            			dataType: "json",
	            			contentType: "application/json",
	            			data: {vo_name: vo_name, retry: retryInput.val()}
	            		})
	            		.done(function() {
	            			retryInput.prop("disabled", false);
	            		})
	            		.fail(function(jqXHR) {
							errorMessage(jqXHR);
						});
	            	});

				tbody.append(
					tr.append($("<td></td>").append(deleteBtn))
					  .append($("<td></td>").append($("<span></span>").text(vo_name)))
					  .append($("<td></td>").append(retryForm))
				);
			}
		});
	})
	.fail(function(jqXHR) {
		errorMessage(jqXHR);
	});
}


/**
 * Initializes the global config view
 */
function setupGlobalConfig()
{
	// Display list
	refreshVoConfigList();

	// Attach to vo-add form
	$("#vo-config-add-frm").submit(function(event) {
		var data = $(this).serialize().split("&");
   		console.log(data);
    	var obj={};
    	for(var key in data)
    	{
        	console.log(data[key]);
        	obj[data[key].split("=")[0]] = data[key].split("=")[1];
    	}
        $.ajax({
            url: "/config/global?",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(obj)
        })
        .done(function(data, textStatus, jqXHR) {
            refreshVoConfigList();
            $("#vo-config-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
        .always(function() {
            $("#vo-config-add-frm > i").attr("class", "glyphicon glyphicon-plus");
        });

		$("#vo-config-add-frm > i").attr("class", "glyphicon glyphicon-refresh");

		event.preventDefault();
	});

	// Attach to global form
	$("#global-config-frm").submit(function(event) {
		var data = $(this).serialize().split("&");
   		console.log(data);
    	var obj={};
    	for(var key in data)
    	{
        	console.log(data[key]);
        	obj[data[key].split("=")[0]] = data[key].split("=")[1];
    	}
        $.ajax({
            url: "/config/global?",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(obj)
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
        .always(function() {
            $("#global-config-frm input, #global-config-frm select, #global-config-frm button").prop("disabled", false);
        });

		$("#global-config-frm input, #global-config-frm select, #global-config-frm button").prop("disabled", true);

		event.preventDefault();
	});

	// Autocomplete
	$("#vo-config-add-field-vo").autocomplete({
		source: "/autocomplete/vo"
	});
}
