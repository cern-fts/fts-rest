#!/usr/bin/env python
from datetime import datetime, timedelta
from M2Crypto import X509, RSA, EVP, ASN1
import os
import pytz
import sys


SEEKING_CERT = 0
LOADING_CERT = 1

# Return a list of certificates from the file
def getX509List(file):
	buffer = ""
	x509List = []
	
	fd = open(file, 'r')	
	status = SEEKING_CERT
	for line in fd:
		if line == '-----BEGIN CERTIFICATE-----\n':
			status = LOADING_CERT
			print "Found certificate in chain"
		elif line == '-----END CERTIFICATE-----\n':
			buffer += line
			x509 = X509.load_cert_string(buffer, X509.FORMAT_PEM)
			x509List.append(x509)
			
			print "Loaded", x509.get_subject().as_text()
			
			buffer = ""
			status = SEEKING_CERT
			
		if status == LOADING_CERT:
			buffer += line
				
	del fd
	
	return x509List



# Output file
if len(sys.argv) < 2:
	raise Exception("Need an output file")

output = sys.argv[1]

# Check environment
if 'X509_USER_PROXY' not in os.environ:
	raise Exception("Need X509_USER_PROXY environment")

# Load the proxy
proxyPath = os.environ['X509_USER_PROXY']
print "Loading", proxyPath

x509List  = getX509List(proxyPath)
proxyCert = x509List[0]
expires   = proxyCert.get_not_after().get_datetime()
fullDN    = proxyCert.get_subject().as_text()

print "DN:     ", fullDN
print "Expires:", expires

if expires < datetime.now(pytz.UTC):
	raise Exception("Proxy expired!")

proxyKey = RSA.load_key(proxyPath)
proxyPKey = EVP.PKey()
proxyPKey.assign_rsa(proxyKey)

# Generate request
print "Generating request"

requestKeyPair = RSA.gen_key(1024, 65537)
requestPKey = EVP.PKey()
requestPKey.assign_rsa(requestKeyPair)

request = X509.Request()
request.set_pubkey(requestPKey)

# Ugly hack to get a mutable X509_Name
proxyCert2  = X509.load_cert(proxyPath, X509.FORMAT_PEM)
requestName = proxyCert2.get_subject()
requestName.add_entry_by_txt('CN', 0x1000, 'proxy', len = -1, loc = -1, set = 0)

request.set_subject(requestName)

request.sign(requestPKey, 'sha1')

# Sign
notBefore = ASN1.ASN1_UTCTIME()
notBefore.set_datetime(datetime.now(pytz.UTC))
notAfter  = ASN1.ASN1_UTCTIME()
notAfter.set_datetime(datetime.now(pytz.UTC) + timedelta(hours = 7))

cert = X509.X509()
cert.set_subject(request.get_subject())
cert.set_serial_number(requestName.as_hash())
cert.set_version(proxyCert.get_version())
cert.set_not_before(notBefore)
cert.set_not_after(notAfter)
cert.set_issuer(proxyCert.get_subject())
cert.set_pubkey(request.get_pubkey())
cert.sign(proxyPKey, 'sha1')

outF = open(output, 'wt')
print >>outF, cert.as_pem()
print >>outF, requestKeyPair.as_pem(cipher = None)
for x509 in x509List:
	print >>outF, x509.as_pem()
del outF
