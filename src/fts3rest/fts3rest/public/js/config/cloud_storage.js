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

/** Template as globals */
var template_cloud_storage_entry = null;

/**
 * Save a new storage, or change it
 */
function saveStorage(form)
{
    var msg = {
        storage_name: form.find("input[name='storage-name']").val(),
        service_api_url: form.find("input[name='service-api']").val(),
        app_key: form.find("input[name='app-key']").val(),
        app_secret: form.find("input[name='app-secret']").val()
    };

    console.log(msg);

    return $.ajax({
        url: "/config/cloud_storage?",
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(msg)
    });
}

/**
 * Delete a storage
 */
function deleteStorage(storage_name, div)
{
    div.css("background", "#d9534f");
    $.ajax({
        url: "/config/cloud_storage/" + encodeURIComponent(storage_name),
        type: "DELETE",
        dataType: "json",
        contentType: "application/json"
    })
    .done(function(data, textStatus, jqXHR) {
        div.fadeOut(300, function() {div.remove();})
    })
    .fail(function(jqXHR) {
        errorMessage(jqXHR);
    })
    .always(function() {
        div.css("background", "#ffffff").css("transition", "background .50s ease-in-out");
    });
}

/**
 * Save a user
 */
function saveUser(storage_name, form)
{
    var msg = {
        user_dn: form.find("input[name='user-dn']").val(),
        vo_name: form.find("input[name='vo-name']").val(),
        access_token: form.find("input[name='access-token']").val(),
        access_token_secret: form.find("input[name='access-secret']").val(),
        request_token: form.find("input[name='request-token']").val(),
        request_token_secret: form.find("input[name='request-secret']").val()
    };

    console.log(msg);

    return $.ajax({
        url: "/config/cloud_storage/" + encodeURIComponent(storage_name),
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(msg)
    });
}

/**
 * Delete a user
 */
function deleteUser(storage_name, form)
{
    var user_dn = form.find("input[name='user-dn']").val();
    var vo_name = form.find("input[name='vo-name']").val();
    var id;
    if (user_dn)
        id = encodeURIComponent(user_dn);
    else
        id = encodeURIComponent(vo_name);

    $.ajax({
        url: "/config/cloud_storage/" + encodeURIComponent(storage_name) + "/" + id,
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
 * Refresh the storage list
 */
function refreshCloudStorage()
{
    var parent = $("#storage-list");

    $.ajax({
        headers: {
            Accept : "application/json",
        },
        url: "/config/cloud_storage?",
    })
    .done(function(data, textStatus, jqXHR) {
        parent.empty();
        $.each(data, function(index, storage) {
            var div = $(template_cloud_storage_entry(storage));

            // Attach to the delete button
            var deleteBtn = div.find(".btn-delete");
            deleteBtn.click(function(event) {
                event.preventDefault();
                deleteStorage(storage.storage_name, div);
            });

            // Attach to the save button
            var saveBtn = div.find(".btn-save");
            saveBtn.click(function(event) {
                event.preventDefault();
                saveStorage(div)
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                });
            });

            // Attach to add a user
            var addUserFrm = div.find(".frm-add-user");
            var addUserBtn = addUserFrm.find(".btn-add-user");
            addUserBtn.click(function(event) {
                event.preventDefault();
                saveUser(storage.storage_name, addUserFrm)
                .done(function(data, textStatus, jqXHR) {
                    refreshCloudStorage();
                })
                .fail(function(jqXHR) {
                    errorMessage(jqXHR);
                });
            });

            // Attach to remove and modify a user
            div.find(".user-entry").each(function() {
                var tr = $(this);
                var deleteUserBtn = tr.find(".btn-delete-user");
                deleteUserBtn.click(function(event) {
                    event.preventDefault();
                    deleteUser(storage.storage_name, tr);
                });
                var saveUserBtn = tr.find(".btn-save-user");
                saveUserBtn.click(function(event) {
                    event.preventDefault();
                    saveUser(storage.storage_name, tr)
                });
            });

            parent.append(div);
        });
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
    template_cloud_storage_entry = Handlebars.compile(
        $("#storage-entry-template").html()
    );
}

/**
 * Initializes the SE view
 */
function setupCloudStorage()
{
    compileTemplates();
    refreshCloudStorage();

    // Bind to form
    $("#add-cloud-frm").submit(function(event) {
        event.preventDefault();
        saveStorage($("#add-cloud-frm"))
        .done(function(data, textStatus, jqXHR) {
            $("#add-cloud-frm").trigger("reset");
            refreshCloudStorage();
        })
        .fail(function(jqXHR) {
            errorMessage(jqXHR);
        });
    });
}
