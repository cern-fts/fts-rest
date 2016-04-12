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
        contentType: "application/json"
    })
    .done(function(data, textStatus, jqXHR) {
        tbody.empty();

        $.each(data, function(i, link) {
            var tr = $("<tr></tr>");

            var deleteBtn = $("<button class='btn btn-link'></button>")
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
              .append($("<td></td>").text(link.symbolicname))
              .append($("<td></td>").text(link.source))
              .append($("<td></td>").text(link.destination))
              .append($("<td></td>").text(link.auto_tuning))
              .append($("<td></td>").text(link.nostreams))
              .append($("<td></td>").text(link.tcp_buffer_size))
              .append($("<td></td>").text(link.urlcopy_tx_to));

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

            var deleteBtn = $("<button class='btn btn-link'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i>");

            deleteBtn.click(function() {
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

            tr.append($("<td></td>").append(deleteBtn))
              .append($("<td></td>").text(share.source))
              .append($("<td></td>").text(share.destination))
              .append($("<td></td>").text(share.vo))
              .append($("<td></td>").text(share.share));

            tbody.append(tr);
        });
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    });
}
/**
 *  * Serializes data to JSON
 *   */
(function ($) {
    $.fn.serializeFormJSON = function () {

        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        }); 
        return o; 
    };
})(jQuery);

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
        $.ajax({
            url: "/config/shares",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: $(this).serializeFormJSON()
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
        $.ajax({
            url: "/config/links",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: $(this).serializeFormJSON()
        })
        .done(function(data, textStatus, jqXHR) {
            refreshLinks();
            $("#link-config-add-frm").trigger("reset");
        })
        .fail(function(jqXHR) {
            alert(jqXHR.responseJSON.message);
        })
        .always(function() {
            $("#link-config-add-frm").prop("disabled", false);
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
