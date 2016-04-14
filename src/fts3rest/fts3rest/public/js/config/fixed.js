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


function refreshFixList()
{
	var tbody = $("#fixed-list");

    $.ajax({
        url: "/config/fixed?",
        contentType: "application/json"
    })
    .done(function(data, textStatus, jqXHR) {
        tbody.empty();

        $.each(data, function(i, fix) {
            var tr = $("<tr></tr>");

            var deleteBtn = $("<button class='btn btn-link'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i>");

            deleteBtn.click(function() {
                tr.css("background", "#d9534f");
                
                var data = {
                        source_se: fix.source_se,
                        dest_se: fix.dest_se,
                        active: 0
                    };
                
			    console.log(data)                 
                $.ajax({
                    url: "/config/fixed",
                    type: "POST",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify(data)
                })
                .done(function(data, textStatus, jqXHR) {
                    tr.fadeOut(300, function() {tr.remove();})
                })
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                    tr.css("background", "#ffffff");
                });
            });

            var changeActiveField = $("<input type='number' class='form-control'></input>")
                .attr("value", fix.active)
                .attr("min", 2);
            changeActiveField.change(function() 
			        var data = {
                            source_se: fix.source_se,
                            dest_se: fix.dest_se,
                            active: changeActiveField.val()
                        };
			   		console.log(data);
			    	  		
                    $.ajax({
                        url: "/config/fixed",
                        type: "POST",
                        dataType: "json",
                        contentType: "application/json",
                        data: JSON.stringify(data)
                    })
                    .done(function(data, textStatus, jqXHR) {
                        tr.css("background", "#ffffff").css("transition", "background .50s ease-in-out");
                    })
                    .fail(function(jqXHR) {
                        alert(jqXHR.responseJSON.message);
                    });

                    tr.css("background", "#5bb75b");
                });

            tr.append($("<td></td>").append(deleteBtn))
              .append($("<td></td>").text(fix.source_se))
              .append($("<td></td>").text(fix.dest_se))
              .append($("<td></td>").append(changeActiveField));
            tbody.append(tr);
        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}


function setupFixed()
{
	// Refresh
	refreshFixList();
	
	
    // Attach to forms
    $("#fixed-add-frm").submit(function(event) {
    	var data = $(this).serialize().split("&");
   		console.log(data);
    	var obj={};
    	for(var key in data)
    	{
        	console.log(data[key]);
        	obj[data[key].split("=")[0]] = data[key].split("=")[1];
    	}
    	console.log(obj)
        $.ajax({
            url: "/config/fixed",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(obj)
        })
        .done(function(data, textStatus, jqXHR) {
            refreshFixList();
            $("#fixed-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
        .always(function() {
            $("#fixed-add-frm input").prop("disabled", false);
            $("#fixed-add-frm input> i").attr("class", "glyphicon glyphicon-plus");
        });

        $("#fixed-add-frm input").prop("disabled", true);
        $("#fixed-add-frm input>i").attr("class", "glyphicon glyphicon-refresh");

        event.preventDefault();
    });

	// Autocomplete
	$("#fixed-add-field-source").autocomplete({
		source: "/autocomplete/source"
	});
	$("#fixed-add-field-destination").autocomplete({
		source: "/autocomplete/destination"
	});
}
