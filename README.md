FTS3-REST
=========
This is the FTS3 RESTful API.
For more detailed information about installation, usage, etc... please, check the [docs](docs/README.md) subdirectory.

## Vagrant
This repository contains a [Vagrantfile](https://www.vagrantup.com/) to make easier to develop.
Please, check [Vagran't install documentation](https://www.vagrantup.com/docs/installation/) to see how to get it
for your platform.

Once you have Vagrant on your machine, just type `vagrant up` and you will have a running fts-rest instance on
your machine. The server's port 8446 will be forwarded to the host, so you will be able to access using
`https://localhost:8446`. Mind that it will use at first a self-signed certificate. If you want a real certificate,
you will have to override the files `hostcert.pem` and `hostkey.pem` inside `/etc/grid-security` on the Vagrant
virtual machine.

To get the server to talk to the rest of an FTS3 system, you will need to copy the file `/etc/fts3/fts3config`
from the FTS3 node, to your Vagrant VM, and restart `httpd`.

## Contacts
If you want to be informed about the FTS3 service in general, including documentation, guies,
new releases, bugfixes, etc.

<http://fts3-service.web.cern.ch/>

If you want to check the roadmap, pending issues, incoming features:

<https://its.cern.ch/jira/browse/FTS/component/12303>

If you want to report a bug, request new functionality, or ask for support:

<mailto:fts-devel@cern.ch>

## Licensing
Please see the file called LICENSE.

