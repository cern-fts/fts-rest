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
 * Save changes
 */
function handleActivityShareSave(form)
{
    var setup = {};
    var vo = form.find("input[name='vo']").val();

    var tbody = form.find(".share-list");
    var rows = tbody.find("tr");
    var shares = {};

    rows.each(function (i, tr) {
        var share = $(tr).find("input[name='share']").val()
        var weight = $(tr).find("input[name='weight']").val();
        shares[share] = parseFloat(weight);
    });


    var msg = {
        'vo': vo,
        'share': shares,
        'active': true
    };
    console.log(msg);

    return $.ajax({
        url: "/config/activity_shares",
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(msg)
    });
}

/**
 * Add a new share to the tbody
 */
function addShare(form, tbody)
{
    var share = form.find("input[name='share']").val()
    var weight = form.find("input[name='weight']").val()

    if (!share || !weight)
        return;

    var tr = $("<tr></tr>");

    var deleteBtn = $("<a class='btn btn-link' id='activity-share-delete-entry-btn'><i class='glyphicon glyphicon-trash'></i></a>");

    tr.append($("<td></td>").append(deleteBtn))
        .append($("<td></td>")
            .append($("<input type='text' name='share' class='form-control' pattern='^[^\s]+$' title='Space is not allowed'/>").val(share))
        )
        .append($("<td></td>")
            .append($("<input type='number' step='0.01' name='weight' class='form-control' min='0' max='1'/>").val(weight))
        );

    tbody.append(tr);

    deleteBtn.click(function(event) {
        tr.remove()
    });

    form.find("input[name='share']").val("");
    form.find("input[name='weight']").val("");

    form.find("input[name='share']").focus();
}

/**
 * Updates the list of activity shares configured
 */
function refreshActivityShares()
{
    var parent = $("#activity-shares-list");
    var tr = $("<tr></tr>");

    $.ajax({
        headers: {
            Accept : "application/json",
        },
        url: "/config/activity_shares?",
    })
    .done(function(data, textStatus, jqXHR) {
        parent.empty();

        $.each(data, function(voName, shareConfig) {
            var div = $("<div class='panel panel-info' name='panel_"+voName+"'></div>");

            var deleteBtn = $("<button class='btn btn-danger' name='delete_" + voName +"'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i> Delete");

            deleteBtn.click(function(event) {
                div.css("background", "#d9534f");
                $.ajax({
                    url: "/config/activity_shares/" + encodeURIComponent(voName),
                    contentType: "application/json",
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

            var submitBtn = $("<button class='btn btn-primary' name='save_" +voName +"'>Save</button>");

            var shareTable = $("<table class='table'></table>");
            var shareTbody = $("<tbody class='share-list'></tbody>");

            $.each(shareConfig.share, function(share, weight) {
                var tr = $("<tr></tr>");
                var shareDeleteBtn = $("<a class='btn btn-link' id='delete-entry-for-saved' name='del_"+share+"'><i class='glyphicon glyphicon-trash'></i></a>");
                shareDeleteBtn.click(function(event) {
                    event.preventDefault();
                    tr.remove()
                });

	      shareval = "<input type='text' name='share' class='form-control' value='"+ share + "' pattern='^[^\s]+$' title='Space is not allowed'/>";
	      weightval = "<input type='number' step='0.01' name='weight' class='form-control' min ='0' max='1'  value='" + weight + "'/>";
              tr.append(
                    $("<td></td>").append(shareDeleteBtn)
                ).append(
                    $("<td></td>").append($(shareval).val(share))
                ).append(
                    $("<td></td>").append($(weightval).val(weight))
                );

                shareTbody.append(tr);
            });

            shareTable.append($("<thead><tr><th></th><th>Activity name</th><th>Weight</th></tr></thead>"));
            shareTable.append(shareTbody);

            var addOpBtn = $("<a class='btn btn-link' id='add-entry-for-saved'><i class='glyphicon glyphicon-plus'></i></a>");

            var addForm = $("<tbody></tbody>")
                .append($("<tr></tr>")
                    .append($("<td></td>").append(addOpBtn))
                    .append($("<td></td>")
                        .append($("<input type='text' name='share' class='form-control' id='share-add-for-saved' pattern='^[^\s]+$' title='Space is not allowed'/></td>"))
                    )
                    .append("<td><input type='number' step='0.01' name='weight' class='form-control' id='weight-add-for-saved' min='0' max='1'/></td>")
                );

            addOpBtn.click(function(event) {
                event.preventDefault();
                addShare(addForm, shareTable)
            });

            bindMethodToEnterOnInput(addForm, function(event) {
                addShare(addForm, shareTable);
            });

            shareTable.append(addForm);

            var form = $("<form class='panel-body' name='" + voName + "'></form>")
                .append($("<input type='hidden' name='vo'/>").val(voName))
                .append(shareTable)
                .append($("<div class='panel-footer'></div>").append(submitBtn).append(deleteBtn));

            form.submit(function(event) {
                event.preventDefault();
                div.css("background", "#5cb85c");
                handleActivityShareSave(form)
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                })
                .always(function() {
                     div.css("background", "#ffffff").css("transition", "background .50s ease-in-out");
                });
            });

            var h2 = $("<h2 class='panel-title'></h2>").text(voName);
            var header = $("<div class='panel-heading'></div>").append(h2);

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
 * Initializes the activity shares view
 */
function setupActivityShares()
{
    // Refresh list
    refreshActivityShares();

    // Bind to form
    bindMethodToEnterOnInput($("#activity-share-add-entry-frm"), function (event) {
        addShare($("#activity-share-add-entry-frm"), $("#activity-share-add-list"));
    });

    $("#activity-share-add-frm").submit(function(event) {
        event.preventDefault();
        handleActivityShareSave($("#activity-share-add-frm"))
        .done(function(data, textStatus, jqXHR) {
	   $(".share-list td").trigger("reset"); 
           refreshActivityShares();
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
	.always(function(){
	$("#activity-share-add .share-list tr").remove();
});
    });

    $("#activity-share-add-entry-btn").click(function(event) {
        addShare($("#activity-share-add-entry-frm"), $("#activity-share-add-list"));
        event.preventDefault();
    })

    // Autocomplete
    $("#activity-share-add-field-vo").autocomplete({
        source: "/autocomplete/vo"
    });
}

