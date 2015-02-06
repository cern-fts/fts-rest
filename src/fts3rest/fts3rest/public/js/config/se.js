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


function refreshSeConfig()
{
	var tbody = $("#se-list");

    $.ajax({
        url: "/config/se?"
    })
    .done(function(data, textStatus, jqXHR) {
        tbody.empty();

        $.each(data, function(se, config) {
            var tr = $("<tr></tr>");

            var deleteBtn = $("<button class='btn btn-link'></button>")
                .append("<i class='glyphicon glyphicon-trash'></i>");

            deleteBtn.click(function() {
                tr.css("background", "#d9534f");
                $.ajax({
                    url: "/config/links/" + encodeURIComponent(link.symbolicname),
                    type: "DELETE"
                })
                .done(function(data, textStatus, jqXHR) {
                    tr.fadeOut(300, function() {tr.remove();})
                })
                .fail(function(jqXHR) {
                    alert(jqXHR.responseJSON.message);
                    tr.css("background", "#ffffff");
                });
            });

            tr.append($("<td></td>").append(deleteBtn))
              .append($("<td></td>").text(se))
              .append($("<td></td>"))
              .append($("<td></td>"))
              .append($("<td></td>"));

            tbody.append(tr);
        });
    })
    .fail(function(jqXHR) {
        alert(jqXHR.responseJSON.message);
    });
}

/*
{
  "test.cern.ch": {
    "as_destination": {
      "active": null, 
      "ipv6": false, 
      "throughput": null, 
      "udt": false
    }, 
    "as_source": {
      "active": null, 
      "ipv6": false, 
      "throughput": null, 
      "udt": false
    }, 
    "operations": {
      "atlas": {
        "delete": 20
      }
    }
  }
  */

function setupSe()
{
	// Refresh list
	refreshSeConfig();

	// Bind to form
	$("se-add-frm").submit(function(event) {

	});

	// Autocomplete
}