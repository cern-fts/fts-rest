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
 * Returns a form-group containing the label and the input
 * with the given parameters
 */
function generateField(name, label, type, value)
{
    return $("<div class='form-group'></div>")
        .append($("<label></label>").text(label))
        .append($("<input class='form-control'></input>")
            .attr("name", name).attr("type", type).val(value)
        );
}


/**
 * Returns a form-group containing a select with Yes/No values
 */
function generateFlagField(name, label, value)
{
    return $("<div class='form-group'></div>")
        .append($("<label></label>").text(label))
        .append($("<select class='form-control'></select>")
            .attr("name", name)
            .append("<option value='true'>Yes</option><option value='false'>No</option>")
            .val(value.toString())
        );
}


/**
 * Returns a form with the given klass and title, prefilled
 * with the values contained in se.
 * Both as_source and as_destination configs are the same, so we avoid duplication here
 */
function generateSubForm(klass, title, se)
{
    var bodyDiv = $("<div class='panel-body'></div>");
    var innerDiv = $("<div class='panel-heading'></div>")
        .append($("<h3 class='panel-title'></h3>").text(title));
    var outerDiv = $("<div class='panel panel-default'></div>")
        .append(innerDiv)
        .append(bodyDiv)
        .addClass(klass);

    bodyDiv.append(generateField("active", "Active limit", "number", se.active))
        .append(generateField("throughput", "Throughput limit (MB/s)", "number", se.throughput))
        .append(generateFlagField("ipv6", "IPv6", se.ipv6))
        .append(generateFlagField("udt", "UDT", se.udt));

    return $("<div class='col-md-6'></div>").append(outerDiv);
}


/**
 * Returns a form with the operations per vo
 */
function generateOpForm(klass, title, operations)
{
    var bodyDiv = $("<div class='panel-body'></div>");
    var innerDiv = $("<div class='panel-heading'></div>")
        .append($("<h3 class='panel-title'></h3>").text(title));
    var outerDiv = $("<div class='panel panel-default'></div>")
        .append(innerDiv)
        .append(bodyDiv)
        .addClass(klass);

    var tbody = $("<tbody class='ops-list'></tbody>");

    if (operations) {
        $.each(operations, function (vo, op) {
            $.each(op, function(op_name, value) {
                var deleteBtn = $("<a class='btn btn-link'><i class='glyphicon glyphicon-trash'></i></a>");
                var limitField = $("<input type='number' name='limit' class='form-control'/>").val(value);

                var row = $("<tr></tr>")
                    .append($("<td></td>").append(deleteBtn))
                    .append($("<td></td>").text(vo)
                        .append($("<input type='hidden' name='vo'/>").val(vo))
                    )
                    .append($("<td></td>").text(op_name)
                        .append($("<input type='hidden' name='operation'/>").val(op_name))
                    )
                    .append($("<td></td>").append(limitField));

                deleteBtn.click(function(event) {
                    event.preventDefault();
                    limitField.val(-1);
                    row.css("display", "none");
                });

                tbody.append(row);
            });
        });
    }

    var addOpBtn = $("<a class='btn btn-link'><i class='glyphicon glyphicon-plus'></i></a>");

    var addForm = $("<tbody></tbody>")
        .append($("<tr></tr>")
            .append($("<td></td>").append(addOpBtn))
            .append($("<td></td>")
                .append($("<input type='text' name='vo' class='form-control'/></td>").autocomplete({
                    source: "/autocomplete/vo"
                }))
            )
            .append("<td><select name='operation' class='form-control'><option value='delete'>Delete</option><option value='staging'>Staging</option></select></td>")
            .append("<td><input type='number' name='limit' class='form-control'/></td>")
        );

    bindMethodToEnterOnInput(addForm, function(event) {
        addOperation(addForm, tbody);
    });

    addOpBtn.click(function(event) {
        event.preventDefault();
        addOperation(addForm, tbody);
    });

    var table = $("<table class='table'></table>")
        .append($("<thead><tr><th></th><th>VO</th><th>Operation</th><th>Limit</th></tr></thead>"))
        .append(tbody)
        .append(addForm);

    bodyDiv.append(table);

    return outerDiv;
}


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
            .append($("<input type='hidden' name='vo'/>").val(vo))
        )
        .append($("<td></td>").text(op)
            .append($("<input type='hidden' name='operation'/>").val(op))
        )
        .append($("<td></td>")
            .append($("<input type='number' name='limit' class='form-control'/>").val(limit))
        );

    tbody.append(tr);

    deleteBtn.click(function(event) {
        tr.remove()
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

    subset.active = parseInt(subform.find("input[name='active']").val());
    subset.ipv6 = (subform.find("select[name='ipv6']").val() == "true");
    subset.throughput = parseFloat(subform.find("input[name='throughput']").val());
    subset.udt = (subform.find("select[name='udt']").val() == "true");

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
    var setup = {};
    var se = form.find("input[name='se']").val();

    setup.as_source = getSubForm(form, 'as-source');
    setup.as_destination = getSubForm(form, 'as-destination');
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
    });
}


/**
 * Updates the list of storages configured
 */
function refreshSeConfig()
{
    var parent = $("#se-list");

    $.ajax({
        url: "/config/se?"
    })
    .done(function(data, textStatus, jqXHR) {
        parent.empty();

        $.each(data, function(se, config) {
            var div = $("<div class='panel panel-info panel-collapse'></div>");

            var deleteBtn = $("<button class='btn btn-danger'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i> Delete");

            deleteBtn.click(function(event) {
                div.css("background", "#d9534f");
                $.ajax({
                    url: "/config/se?se=" + encodeURIComponent(se),
                    type: "DELETE"
                })
                .done(function(data, textStatus, jqXHR) {
                    div.fadeOut(300, function() {tr.remove();})
                })
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                })
                .always(function() {
                     div.css("background", "#ffffff").css("transition", "background .50s ease-in-out");
                });
                event.preventDefault();
            });

            var submitBtn = $("<button class='btn btn-primary'>Save</button>");

            var form = $("<form class='panel-body'></form>")
                .append($("<input type='hidden' name='se'/>").val(se))
                .append($("<div class='row'></div>")
                    .append(generateSubForm("as-source", 'As source', config.as_source))
                    .append(generateSubForm("as-destination", 'As destination', config.as_destination))
                )
                .append(generateOpForm("operations", 'Operations', config.operations))
                .append($("<div class='panel-footer'></div>").append(submitBtn).append(deleteBtn));

            form.submit(function(event) {
                event.preventDefault();
                div.css("background", "#5cb85c");
                handleSeSave(form)
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                })
                .always(function() {
                     div.css("background", "#ffffff").css("transition", "background .50s ease-in-out");
                });
            });

            var h2 = $("<h2 class='panel-title'></h2>").text(se);
            var header = $("<div class='panel-heading'></div>").append(h2);

            header.css("cursor", "pointer");
            header.click(function (event) {
                div.toggleClass("panel-collapse");
                div.toggleClass("panel-info panel-primary");
            });

            div.append(header)
                .append(form);

            parent.append(div);
        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}


/**
 * Initializes the SE view
 */
function setupSe()
{
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
    $("#se-add-field-vo").autocomplete({
        source: "/autocomplete/vo"
    });
}
