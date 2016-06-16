Delegation using command line tools
===================================

The general idea of delegation is as follows:

1. The client asks for delegation to start
2. The server generates a certificate request and its corresponding private key
  * The private key is stored in the database, and the certificate sent to the client
3. The client signs the certificate request
4. The client puts the certificate request into the server
5. The server stores the new certificate together with the private key

So let's cover the client steps one by one

Get our delegation ID
---------------------
`curl -E "${X509_USER_PROXY}" --cacert "${X509_USER_PROXY}"--capath /etc/grid-security/certificates https://fts3-devel.cern.ch:8446/whoami`
```json
{
  "delegation_id": "2d19e65bb16481cf", 
  "dn": [
    "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon", 
    "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon/CN=proxy"
  ], 
  "level": {
    "config": "all", 
    "transfer": "vo"
  }, 
  "roles": [], 
  "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon", 
  "voms_cred": [], 
  "vos": [
    "AlejandroAlvarezAyllon@cern.ch"
  ]
}
```
`2d19e65bb16481cf` in this case must be used for the following requests.

Check if we need to delegate
----------------------------
`curl -E "${X509_USER_PROXY}" --cacert "${X509_USER_PROXY}" --capath /etc/grid-security/certificates https://fts3-devel.cern.ch:8446/delegation/2d19e65bb16481cf`

If you get null, you need to delegate. If you get a termination_time in the past, you need to delegate. Otherwise, is it
up to you to decide if the proxy is long lived enough!

Get a request
-------------
`curl -E "${X509_USER_PROXY}" --cacert "${X509_USER_PROXY}" --capath /etc/grid-security/certificates https://fts3-devel.cern.ch:8446/delegation/2d19e65bb16481cf/request > request.pem`

You can know have a look into the request, if you like

```
$ openssl req -in request.pem -noout -text
Certificate Request:
    Data:
        Version: 0 (0x0)
        Subject: O=Dummy
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (1024 bit)
                Modulus:
                    00:d9:ee:db:bc:7e:df:74:12:33:e0:63:d9:1d:75:
                    20:fa:27:cf:73:0f:3a:28:5f:78:46:c3:20:ed:be:
                    ac:12:88:e9:42:c7:24:76:29:8f:e4:ef:7a:21:b7:
                    0d:ae:48:15:b4:fb:69:ae:d6:16:bf:08:1f:de:bf:
                    47:21:11:e3:cc:12:ab:00:68:d6:70:98:89:a3:55:
                    75:59:d5:bc:a8:a0:ea:70:2c:df:cd:97:11:c4:aa:
                    c3:8b:be:5b:ce:ba:f2:10:50:b9:1b:9d:a1:91:18:
                    9a:cf:0f:5c:b5:33:9d:93:5e:ae:e0:f5:83:ad:b2:
                    1e:30:fb:3c:c8:45:91:e7:ed
                Exponent: 65537 (0x10001)
        Attributes:
            a0:00
    Signature Algorithm: md5WithRSAEncryption
         49:1f:00:42:e1:3d:b5:8b:52:9c:a4:d9:ef:55:21:d5:cd:56:
         56:c6:82:08:6f:70:2e:91:cc:2f:64:e6:6f:fe:c3:8d:08:fa:
         a3:fa:6d:76:97:d0:05:b5:da:17:83:18:9a:93:eb:13:3b:3d:
         17:67:2c:77:d2:eb:02:6a:6a:10:53:e8:a9:25:8a:e8:cf:77:
         ea:0b:fa:6b:e9:65:96:12:d7:aa:94:79:dc:f9:2c:5a:3c:94:
         c6:fc:eb:08:c4:8d:47:14:52:db:1f:f7:53:12:f6:05:4e:43:
         a7:88:4f:1f:ba:dc:d9:c1:c3:d7:4b:86:68:14:33:bb:76:2a:
         51:9d
```

You can see that the subject does *not* match your DN. You will need to set it properly when signing.

Sign the request
----------------
This is the bit that's hard to remember

```
$ cp /etc/pki/tls/openssl.cnf .
$ SUBJECT=`openssl x509 -in ~/proxy.pem -noout -subject | grep '/.*' -o`
$ mkdir -p demoCA/newcerts
$ touch demoCA/index.txt
$ echo "00000000000000000000" > demoCA/serial
$ openssl ca -config openssl.cnf -policy policy_anything -keyfile ~/proxy.pem -cert ~/proxy.pem -in request.pem -subj "$SUBJECT/CN=proxy" -days 1 -batch -out newproxy.pem
```

Remember you can specify as a parameter the lifetime of the new certificate!
You may need to add manually to openssl.cnf, under \[policy_anything\] `domainComponent=optional`
Remember to indicate in the openssl.cnf the demoCA directory or create the files in /etc/pki/CA.
You can double check the output using openssl again.

```
$ openssl x509 -in newproxy.pem -noout -text
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 7 (0x7)
    Signature Algorithm: sha256WithRSAEncryption
        Issuer: DC=ch, DC=cern, OU=Organic Units, OU=Users, CN=aalvarez, CN=678984, CN=Alejandro Alvarez Ayllon, CN=proxy
        Validity
            Not Before: Jun 26 14:29:19 2014 GMT
            Not After : Jun 26 14:29:19 2015 GMT
        Subject: DC=ch, DC=cern, OU=Organic Units, OU=Users, CN=aalvarez, CN=678984, CN=Alejandro Alvarez Ayllon, CN=proxy, CN=proxy
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (1024 bit)
                Modulus:
                    00:d9:ee:db:bc:7e:df:74:12:33:e0:63:d9:1d:75:
                    20:fa:27:cf:73:0f:3a:28:5f:78:46:c3:20:ed:be:
                    ac:12:88:e9:42:c7:24:76:29:8f:e4:ef:7a:21:b7:
                    0d:ae:48:15:b4:fb:69:ae:d6:16:bf:08:1f:de:bf:
                    47:21:11:e3:cc:12:ab:00:68:d6:70:98:89:a3:55:
                    75:59:d5:bc:a8:a0:ea:70:2c:df:cd:97:11:c4:aa:
                    c3:8b:be:5b:ce:ba:f2:10:50:b9:1b:9d:a1:91:18:
                    9a:cf:0f:5c:b5:33:9d:93:5e:ae:e0:f5:83:ad:b2:
                    1e:30:fb:3c:c8:45:91:e7:ed
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            X509v3 Basic Constraints: 
                CA:FALSE
            Netscape Comment: 
                OpenSSL Generated Certificate
            X509v3 Subject Key Identifier: 
                9C:1A:36:32:73:DF:06:09:7C:1E:63:D2:F8:6D:41:E1:B1:76:60:0D
            X509v3 Authority Key Identifier: 
                DirName:/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon
                serial:57:32:5B:25:00:02:00:02:24:AE

    Signature Algorithm: sha256WithRSAEncryption
         9c:7c:20:7d:44:ef:6e:44:e8:e6:72:a0:31:5e:54:57:12:a1:
         71:d6:a8:7d:12:ca:1b:a5:90:b0:3e:2a:da:4a:60:7c:16:4a:
         ae:8c:0f:ca:48:10:5a:43:f5:63:3b:a0:cb:7b:35:c1:f6:7a:
         b1:61:d1:2e:82:3e:ca:11:97:9d:36:6b:90:c9:91:42:40:3a:
         02:5f:45:60:8a:a5:4e:de:ab:77:15:96:11:a0:82:e2:ad:79:
         e9:fb:dd:5e:79:0b:34:7d:2f:81:53:09:62:73:de:69:bf:71:
         7c:4e:2f:44:1f:b7:40:18:87:31:95:47:a0:2d:96:43:be:93:
         5a:a2
```

Build the full proxy
--------------------
We need to append the signing proxy (without the private key), and to remove the additional information openssl has put into newproxy.pem
```
$ openssl x509 -in newproxy.pem > fullproxy.pem
$ sed -e '/-----BEGIN CERTIFICATE-----/,/----END CERTIFICATE-----/!d' ~/proxy.pem >> fullproxy.pem
```

Upload the proxy
----------------
```
$ curl -E "${X509_USER_PROXY}" --cacert "${X509_USER_PROXY}" --capath /etc/grid-security/certificates https://fts3-devel.cern.ch:8446/delegation/2d19e65bb16481cf/credential -T fullproxy.pem
```

And you can now double check

`curl -E "${X509_USER_PROXY}" --cacert "${X509_USER_PROXY}"--capath /etc/grid-security/certificates https://fts3-devel.cern.ch:8446/delegation/2d19e65bb16481cf`
```json
{
  "termination_time": "2014-06-27T14:32:00"
}
```
