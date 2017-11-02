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

var globalConfigRowHtml = '\
<tr> \
    <td> \
        <button class="btn btn-link bt-delete" type="button" title="Delete" id="button_delete_global"> \
            <i class="glyphicon glyphicon-trash"></i> \
        </button> \
        <button class="btn btn-link bt-save" type="button" title="Save" id="button_save_global"> \
            \<i class="glyphicon glyphicon-floppy-disk"></i> \
        </button> \
    </td> \
    <td class="vo_name"> \
        VO NAME \
    </td> \
    <td> \
        <input type="number" name="retry" min="0" max="10" class="form-control"/> \
    </td> \
    <td> \
        <input type="number" name="global_timeout" class="form-control" min="0"/> \
    </td> \
    <td> \
        <input type="number" name="max_time_queue" class="form-control" min="0"/> \
    </td> \
    <td> \
        <input type="number" name="sec_per_mb" class="form-control" min="0"/> \
    </td> \
    <td> \
        <select name="show_user_dn" id="show_user_dn" class="form-control"> \
            <option value="true">Yes</option> \
            <option value="false">No</option> \
        </select> \
    </td> \
</tr>';


/**
 * Updates the list of configured globals per VO
 */
function refreshVoConfigList()
{
	var tbody = $("#vo-config-list");

	$.ajax({
		headers: {
            Accept : "application/json",
        },
		url: "/config/global?",
	})
	.done(function(data, textStatus, jqXHR) {
		tbody.empty();

		$.each(data, function(vo_name, vo) {
            var tr = $(globalConfigRowHtml);

            tr.find(".vo_name").text(vo_name);
            $.each(vo, function(op_name, op_value) {
		tr.attr('name',vo.vo_name);
		tr.find("button[id='button_delete_global']").attr('name', vo.vo_name);
		tr.find("input[name='" + op_name + "']").each(function(){
		 $(this).attr('value',op_value);
                });
		tr.find("select[name='" + op_name + "']").each(function(){
                 $(this).attr('value',op_value.toString());
		 tr.find("select[name='" + op_name + "']").val(op_value.toString());
                });
		
            });


            tr.find(".bt-delete").click(function() {
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

            tr.find(".bt-save").click(function() {
                var ret_wrong = tr.find("input[name='retry']");
                var max_wrong = tr.find("input[name='max_time_queue']");
                var glo_wrong = tr.find("input[name='global_timeout']");
                var sec_wrong = tr.find("input[name='sec_per_mb']");
                tr.find("input").prop("disabled", true);
                tr.find("select").prop("disabled", true);
                tr.css("background", "#3c763d");

		if ((tr.find("input[name='retry']").val() > 10)||(tr.find("input[name='retry']").val() < 0) ||(tr.find("input[name='max_time_queue']").val() < 0)||(tr.find("input[name='global_timeout']").val() < 0)||(tr.find("input[name='sec_per_mb']").val() < 0)){ 
		    errorMessage(jqXHR);
                    tr.find("input").prop("disabled", false);
                    tr.find("select").prop("disabled", false);
                    tr.css("background", "#ffffff");
                    ret_wrong.val(encodeURIComponent(vo.retry));
                    max_wrong.val(encodeURIComponent(vo.max_time_queue));
                    glo_wrong.val(encodeURIComponent(vo.global_timeout));
                    sec_wrong.val(encodeURIComponent(vo.sec_per_mb));
		}
		else{
                $.ajax({
                    url: "/config/global?",
                    type: "POST",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({
                        vo_name: vo_name,
                        retry: tr.find("input[name='retry']").val(),
                        max_time_queue: tr.find("input[name='max_time_queue']").val(),
                        global_timeout: tr.find("input[name='global_timeout']").val(),
                        sec_per_mb: tr.find("input[name='sec_per_mb']").val(),
                        show_user_dn: tr.find("select[name='show_user_dn']").val()
                    })
                })
                .done(function() {
                    tr.css("background", "none");
                    tr.find("input").prop("disabled", false);
                    tr.find("select").prop("disabled", false);
                })
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                    tr.find("input").prop("disabled", false);
                    tr.find("select").prop("disabled", false);
                    tr.css("background", "#ffffff");
                    ret_wrong.val(encodeURIComponent(vo.retry));
                    max_wrong.val(encodeURIComponent(vo.max_time_queue));
                    glo_wrong.val(encodeURIComponent(vo.global_timeout));
                    sec_wrong.val(encodeURIComponent(vo.sec_per_mb));
                })};
            });

            tbody.append(tr);
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
        	console.log(decodeURIComponent(data[key]));
        	obj[decodeURIComponent(data[key].split("=")[0])] = decodeURIComponent(data[key].split("=")[1]);
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
