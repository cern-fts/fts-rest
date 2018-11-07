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
 * Updates the list of link configurations
 */
function refreshLinks()
{
    var tbody = $("#link-config-list");
    $.ajax({
        url: "/config/links?",
        headers: {
            Accept : "application/json",
        },
    })
    .done(function(data, textStatus, jqXHR) {
        tbody.empty();

        $.each(data, function(i, link) {
            var tr = $("<tr></tr>");

            var deleteBtn = $("<button class='btn btn-link' type='button'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i>");

            deleteBtn.click(function() {
                tr.css("background", "#d9534f");
                $.ajax({
                    url: "/config/links/" + encodeURIComponent(link.symbolicname),
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
 
            var updateBtn = $("<button class='btn btn-link' type='button'></button>")
                .append("<i class='glyphicon glyphicon-floppy-disk'></i>");  

            tr.append($("<td></td>").append(deleteBtn))
              .append($("<td></td>").append(updateBtn))
              .append($("<td></td>")
              .append($("<input type='text' name='symbolicname' class='form-control'/>").val(link.symbolicname)))
              .append($("<td></td>")
              .append($("<input type='text' name='source' class='form-control'/>").val(link.source)))
              .append($("<td></td>")
              .append($("<input type='text' name='destination' class='form-control'/>").val(link.destination)))
              .append($("<td></td>")
              .append($("<input type='number' name='nostreams' min='0' max='16' class='form-control'/>").val(link.nostreams)))
              .append($("<td></td>")
              .append($("<input type='number' name='min_active' class='form-control'/>").val(link.min_active)))
              .append($("<td></td>")
              .append($("<input type='number' name='max_active' class='form-control'/>").val(link.max_active)))
              .append($("<td></td>")
              .append($("<input type='number' name='optimizer_mode' min='0' max='3' class='form-control'/>").val(link.optimizer_mode)))
              .append($("<td></td>")
              .append($("<input type='number' name='tcp_buffer_size' class='form-control'/>").val(link.tcp_buffer_size)));
           tbody.append(tr);

                updateBtn.click(function() {
                  //  tr.css("background", "#3CB371");
                    var saveload = {
                        symbolicname: tr.find("input[name='symbolicname']").val(),
                        source: tr.find("input[name='source']").val(),
                        destination: tr.find("input[name='destination']").val(),
                        nostreams: tr.find("input[name='nostreams']").val(),
                        min_active: tr.find("input[name='min_active']").val(),
                        max_active: tr.find("input[name='max_active']").val(),
                        optimizer_mode: tr.find("input[name='optimizer_mode']").val(),
                        tcp_buffer_size: tr.find("input[name='tcp_buffer_size']").val()
                    };
                    console.log(saveload);
                    $.ajax({
                        url: "/config/links",
                        type: "POST",
                        dataType: "json",
                        contentType: "application/json",
                        data: JSON.stringify(saveload)
                    })
                    .done(function() {
                        tr.find("input").prop("disabled", false)
		   	tr.css("background", "#3CB371");
			refreshLinks();

                    })
                    .fail(function(jqXHR) {
                        errorMessage(jqXHR);
                        tr.css("background", "#ffffff");
                    });
              });
        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });

}


/**
 * Updates the list of share configurations
 */
function refreshShares()
{
    var tbody = $("#share-list");

    $.ajax({
        url: "/config/shares?",
        contentType: "application/json"
    })
    .done(function(data, textStatus, jqXHR) {
        tbody.empty();

        $.each(data, function(i, share) {
            var tr = $("<tr></tr>");
	    var deleteBtn = $("<a class='btn btn-link'><i class='glyphicon glyphicon-trash'></i></a>");


            tr.append($("<td></td>").append(deleteBtn))
               .append($("<td></td>").text(share.source)
               .append($("<input type='hidden' name='source'/>").val(share.source)))
               .append($("<td></td>").text(share.destination)
               .append($("<input type='hidden' name='destination'/>").val(share.destination)))
               .append($("<td></td>").text(share.vo)
               .append($("<input type='hidden' name='vo'/>").val(share.vo)))
               .append($("<td></td>")
               .append($("<input type='number' name='share' class='form-control'/>").val(share.share))
        	);
	    tbody.append(tr);

            deleteBtn.click(function(event) {
                tr.css("background", "#d9534f");
                $.ajax({
                    url: "/config/shares?source=" + encodeURIComponent(share.source)
                        + "&destination=" + encodeURIComponent(share.destination)
                        + "&vo=" + encodeURIComponent(share.vo),
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

        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}


/**
 * Initialize the links view
 */
function setupLinks()
{
    // Refresh lists
    refreshLinks();
    refreshShares();

    // Attach to forms
    $("#share-add-frm").submit(function(event) {
        var addFrm = $("#share-add-frm");
        var payload = {
            source: addFrm.find("[name=source]").val(),
            destination: addFrm.find("[name=destination]").val(),
            vo: addFrm.find("[name=vo]").val(),
            share: addFrm.find("[name=share]").val(),
        };
        console.log(payload);

        $.ajax({
            url: "/config/shares",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(payload)
        })
        .done(function(data, textStatus, jqXHR) {
            refreshShares();
            $("#share-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        })
        .always(function() {
            $("#share-add-frm input").prop("disabled", false);
            $("#share-add-frm input> i").attr("class", "glyphicon glyphicon-plus");
        });

        $("#share-add-frm input").prop("disabled", true);
        $("#share-add-frm input>i").attr("class", "glyphicon glyphicon-refresh");

        event.preventDefault();
    });

    $("#link-config-add-frm").submit(function(event) {
        var addFrm = $("#link-config-add-frm");
        var payload = {
            symbolicname: addFrm.find("[name=symbolicname]").val(),
            source: addFrm.find("[name=source]").val(),
            destination: addFrm.find("[name=destination]").val(),

            max_active: addFrm.find("[name=max_active]").val(),
            optimizer_mode: addFrm.find("[name=optimizer_mode]").val(),
            tcp_buffer_size: addFrm.find("[name=tcp_buffer_size]").val(),
        };
        console.log(payload);

        $.ajax({
            url: "/config/links",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(payload)
        })
        .done(function(data, textStatus, jqXHR) {
            refreshLinks();
            refreshShares();
            $("#link-config-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            alert(jqXHR.responseJSON.message);
        })
        .always(function() {
            $("#link-config-add-frm input").prop("disabled", false);
            $("#link-config-add-frm>i").attr("class", "glyphicon glyphicon-plus");
        });

        $("#link-config-add-frm input").prop("disabled", true);
        $("#link-config-add-frm>i").attr("class", "glyphicon glyphicon-refresh");

        event.preventDefault();
    });

    // Autocomplete
    $("#link-add-field-source").autocomplete({
        source: "/autocomplete/source"
    });
    $("#link-add-field-destination").autocomplete({
        source: "/autocomplete/destination"
    });
    $("#share-add-field-source").autocomplete({
        source: "/autocomplete/source"
    });
    $("#share-add-field-destination").autocomplete({
        source: "/autocomplete/destination"
    });
}


