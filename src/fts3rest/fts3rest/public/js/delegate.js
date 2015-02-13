/*
 *  Copyright 2014 CERN
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


/** Perform a simple GET
 * @param url   URL to get
 * @return The raw response body
 */
function httpGET(url)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", url, false);
    xmlHttp.send(null);
    if (xmlHttp.status >= 400)
        throw xmlHttp.statusText;
    return xmlHttp.responseText;
}


/** Perform a PUT
 */
function httpPUT(url, body)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("PUT", url, false);
    xmlHttp.send(body);
    if (xmlHttp.status >= 400)
        throw xmlHttp.statusText;
}


/** Perform a POST of a JSON message
 */
function httpPOST(url, body)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", url, false);
    xmlHttp.setRequestHeader('Content-Type', 'application/json');
    xmlHttp.send(body);
    if (xmlHttp.status >= 400)
        throw xmlHttp.statusText;
}


/** Get the proxy request
 * @param delegationId  Get the proxy request for this delegation id
 * @return An ASN1 object containing the proxy request
 */
function getProxyRequest(delegationId)
{
    var url = "/delegation/" + delegationId + "/request";
    var raw_request = httpGET(url);
    return ProxyJS.Util.pem2asn1(raw_request);
}


/** Put the signed proxy
 */
function putProxy(delegationId, proxy)
{
    var url = "/delegation/" + delegationId + '/credential';
    httpPUT(url, proxy);
}

/** Ask the server to upgrade the proxy with VO extensions
 */
function requestVo(delegationId, voName)
{
    var url = "/delegation/" + delegationId + '/voms';
    var payload = '["' + voName.replace('"', '\\"') + '"]';
    try {
        httpPOST(url, payload);
    }
    catch (err) {
        throw "Failed to generate the proxy for the given VO: " + err.toString();
    }
}

/** Entry point
 * @param delegationId  The delegation ID for the user
 * @param userDn        The user DN
 * @param publicCertPem User"s public certificate, PEM-encoded
 * @param privateKeyPem User"s private key, PEM-encoded
 * @param voName        Upgrade the proxy stored in the server with the credentials for the given VO
 * @param lifetime      Lifetime in hours
 */
function doDelegateInternal(delegationId, userDn, publicCertPem, privateKeyPem, voName, lifetime)
{
    // Load certificate and private key
    var certificate = new X509();
    try {
        certificate.readCertPEM(publicCertPem);
    }
    catch (err) {
        throw "Invalid or malformed X509 user certificate (contact site administrator)";
    }
    console.log("Got valid X509 certificate request with subject " + certificate.getSubjectString() + " and modulus " + certificate.subjectPublicKeyRSA.n);

    var privateKey = new RSAKey();
    try {
        privateKey.readPrivateKeyFromPEMString(privateKeyPem);
    }
    catch (err) {
        throw "Invalid or malformed RSA private key";
    }
    console.log("Got valid RSA private key with modulus " +  privateKey.n);

    // Get the proxy request
    var request = getProxyRequest(delegationId);
    console.log("Got proxy request for " + delegationId);

    // Sign
    var proxy = ProxyJS.signRequest(request, userDn, certificate, privateKey, lifetime);
    var proxyPem = proxy.getPEMString().replace(/\r/g, "").replace(/^\s*$[\n\r]{1,}/gm, "\n");

    // Append certificate
    proxyPem += "\n" + publicCertPem;
	console.log("Signed PEM proxy\n" + proxyPem);

    // Upload
    putProxy(delegationId, proxyPem);

    // If voName, request the server to upgrade with VO credentials
    if (voName)
        requestVo(delegationId, voName);
}


/** Get values from the HTML document and wraps any potential error in a global try/catch
 */
function doDelegate()
{
    try {
        var privateKey = document.getElementById("private-key").value;
        var voName = document.getElementById("vo").value;
        var publicCertificate = httpGET("/whoami/certificate");
        var delegationId = document.getElementById("delegation-id").value;
        var userDn = document.getElementById("user-dn").value;
        var lifetime = parseInt(document.getElementById("lifetime").value);
        if (isNaN(lifetime))
            throw "Invalid value in lifetime";
        if (publicCertificate.length == 0)
            throw "Could not get the public certificate";

        doDelegateInternal(delegationId, userDn, publicCertificate, privateKey, voName, lifetime);

        var delegationDialogBody =  document.getElementById("delegation-dialog-body");
        delegationDialogBody.innerHTML = '<div class="alert alert-success">Delegated successfully for delegation id ' + delegationId + '</div>';

        window.close();
    }
    catch (err) {
        if (typeof(err) == "string")
            alert(err);
        else
            alert(err.message);
    }
}


/** Just closes the window
 */
function cancel()
{
    document.getElementById("private-key").value = "";
    document.getElementById("vo").value = "";
    window.close();
}
