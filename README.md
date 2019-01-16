FTS3-REST
=========
This is the FTS3 RESTful API.
For more detailed information about installation, usage, etc... please, check the [docs](docs/README.md) subdirectory.

## Firewalld: How to set up a firewall using firewalld on centos7

Firewalld is installed by default on some Linux distributions, including many images of CentOS 7. However, it may be necessary for you to install firewalld yourself:

    sudo yum install firewalld

After you install firewalld, you can enable the service and reboot your server. Keep in mind that enabling firewalld will cause the service to start up at boot. It is best practice to create your firewall rules and take the opportunity to test them before configuring this behavior in order to avoid potential issues.

    sudo systemctl enable firewalld
    sudo reboot

When the server restarts, your firewall should be brought up, your network interfaces should be put into the zones you configured (or fall back to the configured default zone), and any rules associated with the zone(s) will be applied to the associated interfaces.

We can verify that the service is running and reachable by typing:

    sudo firewall-cmd --state

output
running

This indicates that our firewall is up and running with the default configuration.

When running fts-rest, we can allow this traffic for interfaces in our "public" zone for this session by copying first fts3rest.xml in /usr/lib/firewalld/services and then typing:

    sudo firewall-cmd --zone=public --add-service=fts-rest

You can leave out the --zone= if you wish to modify the default zone. We can verify the operation was successful by using the --list-all or --list-services operations:

    sudo firewall-cmd --zone=public --list-services


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

