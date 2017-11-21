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

var template_storage = null;

/**
 * Helper function that adds to the given tbody a new row
 * containing the values defined inside the element form
 */
function addOperation(form, tbody)
{
    var vo = form.find("input[name='vo']").val()
    var op = form.find("select[name='operation']").val()
    var limit = form.find("input[name='limit']").val()

    if (!vo || !op || !limit)
        return;

    var tr = $("<tr></tr>");

    var deleteBtn = $("<a class='btn btn-link'><i class='glyphicon glyphicon-trash'></i></a>");

    tr.append($("<td></td>").append(deleteBtn))
        .append($("<td></td>").text(vo)
            .append($("<input type='hidden' name='vo' class='form-control'/>").val(vo))
        )
        .append($("<td></td>").text(op)
            .append($("<input type='hidden' name='operation' class='form-control'/>").val(op))
        )
        .append($("<td></td>")
            .append($("<input type='number' name='limit' class='form-control' min='0'/>").val(limit))
        );

    tbody.append(tr);

    deleteBtn.click(function(event) {
	tr.remove()
	tbody.remove(tr)
    });

    form.find("input[name='vo']").val("");
    form.find("input[name='limit']").val("");

    form.find("input[name='vo']").focus();
}


/**
 * Opposite of generateSubForm
 * Get the values defined in the subform with the class klass contained in
 * form
 */
function getSubForm(form, klass)
{
    var subform = form.find("." + klass);
    var subset = {};
    subset.se_metadata = subform.find("input[name='se_metadata']").val()
    subset.inbound_max_active = parseInt(subform.find("input[name='inbound_max_active']").val());
    subset.outbound_max_active = parseInt(subform.find("input[name='outbound_max_active']").val());
    subset.inbound_max_throughput = parseFloat(subform.find("input[name='inbound_max_throughput']").val());
    subset.outbound_max_throughput = parseFloat(subform.find("input[name='outbound_max_throughput']").val());
    subset.ipv6 = parseInt(subform.find("input[name='ipv6']").val());
    subset.udt = parseInt(subform.find("input[name='udt']").val());
    subset.debug_level = parseInt(subform.find("input[name='debug_level']").val());
    
    return subset;
}


/**
 * Opposite of generateOpsForm
 * Get the values defined in the subform with the class klass contained in
 * form
 */
function getOperations(form, klass)
{
    var tbody = form.find("." + klass);
    var rows = tbody.find("tr");
    var ops = {};

    rows.each(function (i, tr) {
        var vo = $(tr).find("input[name='vo']").val()
        var op = $(tr).find("input[name='operation']").val();
        var limit = parseInt($(tr).find("input[name='limit']").val());

        if (!(vo in ops))
            ops[vo] = {};
        ops[vo][op] = limit;
    });

    return ops;
}


/**
 * Handling saving, both for new entries and updates
 */
function handleSeSave(form)
{
    form.css("background", "#3c763d").css("transition", "none");

    var setup = {};
    var se = form.find("input[name='se']").val();

    setup.se_info = getSubForm(form, 'se-info');
    setup.operations = getOperations(form, 'ops-list');


    var msg = {};
    msg[se] = setup;
    console.log(msg);

    return $.ajax({
        url: "/config/se?",
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(msg)
    })
    .done(function() {
	$("tbody#se-add-ops-list.ops-list tr").remove();
    })
    .always(function() {
        form.css("background", "#ffffff").css("transition", "background .50s ease-in-out");
    });
}


/**
 * Delete a storage
 */
function deleteSe(form)
{
    var se = form.find("input[name='se']").val();

    form.css("background", "#ff0000").css("transition", "background .50s ease-in-out");
    $.ajax({
        url: "/config/se?se=" + encodeURIComponent(se),
        type: "DELETE",
        dataType: "json",
        contentType: "application/json"
    })
    .done(function(data, textStatus, jqXHR) {
        form.fadeOut(300, function() {form.remove();})
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    })
    .always(function() {
        form.css("background", "#ffffff").css("transition", "background .50s ease-in-out");
    });
}

/**
 * Updates the list of storages configured
 */
function refreshSeConfig()
{
    var parent = $("#se-list");

    $.ajax({
        headers: {
            Accept : "application/json",
        },
        url: "/config/se?",
    })
    .done(function(data, textStatus, jqXHR) {
        parent.empty();
        var divs = $(template_storage(data));
        // Attach actions
        $.each(divs, function(index) {
            var div = $(this);

            var header = div.find(".panel-heading");
            header.click(function(event) {
                div.toggleClass("panel-collapse");
            });

            div.find(".se-modify-frm").submit(function(event) {
                event.preventDefault();
                handleSeSave(div)
	        .done(function(data, textStatus, jqXHR) {
                $("#se-save-frm").trigger("reset");
                refreshSeConfig();
                })

                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                });
            });
            div.find(".btn-delete").click(function(event) {
                event.preventDefault();
                deleteSe(div);
            });
            div.find(".frm-set-operation").each(function() {
                var tr = $(this);
                var buttonDelete = tr.find(".btn-delete-operation");
                buttonDelete.click(function(event) {
                    event.preventDefault();
                    tr.remove();
                });
            });
            var opList = div.find(".ops-list");
            var frmAdd = div.find(".frm-add-operation");
            var buttonAdd = frmAdd.find(".btn-add-operation");
            buttonAdd.click(function(event) {
                event.preventDefault();
                addOperation(frmAdd, opList);
            });
        });
        parent.append(divs);
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
    template_storage = Handlebars.compile(
        $("#se-template").html()
    );
}

/**
 * Initializes the SE view
 */
function setupSe()
{
    compileTemplates();

    // Refresh list
    refreshSeConfig();

    bindMethodToEnterOnInput($("#se-add-ops-add"), function(event) {
        addOperation($("#se-add-ops-add"), $("#se-add-ops-list"));
    });

    // Bind to form
    $("#se-add-frm").submit(function(event) {
	event.preventDefault();
        handleSeSave($("#se-add-frm"))
        .done(function(data, textStatus, jqXHR) {
            $("#se-add-frm").trigger("reset");
            refreshSeConfig();
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        });
    });

    $("#se-add-ops-add-btn").click(function(event) {
        addOperation($("#se-add-ops-add"), $("#se-add-ops-list"));
        event.preventDefault();
    })

    // Autocomplete
    $("#se-add-field-se").autocomplete({
        source: "/autocomplete/storage"
    });
}
