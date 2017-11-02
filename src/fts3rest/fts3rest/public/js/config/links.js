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

            var deleteBtn = $("<button class='btn btn-link' type='button' id='button_delete_link' name='lndel_"+link.symbolicname+"'></button>")
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

            tr.append($("<td></td>").append(deleteBtn))
              .append($("<td id='symname'></td>").text(link.symbolicname))
              .append($("<td id='srcname'></td>").text(link.source))
              .append($("<td></td>").text(link.destination))
              .append($("<td></td>").text(link.nostreams))
              .append($("<td></td>").text(link.min_active))
              .append($("<td></td>").text(link.max_active))
              .append($("<td></td>").text(link.optimizer_mode))
              .append($("<td></td>").text(link.tcp_buffer_size))

            tbody.append(tr);
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
	    var deleteBtn = $("<a class='btn btn-link' id='button_delete_share' name='shdel_"+share.source+"_"+share.vo+"'><i class='glyphicon glyphicon-trash'></i></a>");
	    var saveBtn = $("<a class='btn btn-link' id='button_save_share'><i class='glyphicon glyphicon-floppy-disk'></i></a>");
	
            tr.append($("<td></td>").append(deleteBtn, saveBtn))
               .append($("<td id='share_name'></td>").text(share.source)
               .append($("<input type='hidden' name='source-saved'/>").val(share.source)))
               .append($("<td id='dn_name'></td>").text(share.destination)
               .append($("<input type='hidden' name='destination-saved'/>").val(share.destination)))
               .append($("<td id='vo_name'></td>").text(share.vo)
               .append($("<input type='hidden' name='vo-saved'/>").val(share.vo)))
               .append($("<td id='sh_name'></td>")
               .append($("<input type='number' name='share-saved' class='form-control' min='1'/>").val(share.share))
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

            saveBtn.click(function(event) {
		var share_wrong = tr.find("input[name='share-saved']")
		//console.log(encodeURIComponent(share.share))
	        tr.css("background", "#3c763d");
                tr.find("input").prop("disabled", true);
                tr.find("select").prop("disabled", true);
                if (tr.find("input[name='share-saved']").val() < 0){
                    errorMessage(jqXHR);
                    tr.find("input").prop("disabled", false);
                    tr.find("select").prop("disabled", false);
                    tr.css("background", "#ffffff");
                    share_wrong.val(encodeURIComponent(share.share));
                }
                else{

                $.ajax({
                    url: "/config/shares?",
                    type: "POST",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({
                        source: share.source,
			destination: share.destination,
			vo: share.vo,			
                        share: tr.find("input[name='share-saved']").val()
                    })
                })

                .done(function(data, textStatus, jqXHR) {
		    tr.css("background", "none");
                    tr.find("input").prop("disabled", false);
                    tr.find("select").prop("disabled", false);

                })
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
		    tr.find("input").prop("disabled", false);
                    tr.find("select").prop("disabled", false);
		    tr.css("background", "#ffffff");
		    share_wrong.val(encodeURIComponent(share.share))
			    
                })};
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
            nostreams: addFrm.find("[name=nostreams]").val(),
            min_active: addFrm.find("[name=min_active]").val(),
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
	    errorMessage(jqXHR);
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
