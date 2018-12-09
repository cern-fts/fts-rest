#!/bin/bash

cat > /etc/yum.repos.d/dmc.repo <<EOF
[dmc-builds]
name=DMC Continuous Build Repository
baseurl=http://dmc-repo.web.cern.ch/dmc-repo/testing/el\$releasever/\$basearch
gpgcheck=0
enabled=1
protect=1
EOF

cat > /etc/yum.repos.d/egi-trust.repo <<EOF
[carepo]
name=IGTF CA Repository
enabled=1
baseurl=http://linuxsoft.cern.ch/mirror/repository.egi.eu/sw/production/cas/1/current/
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/GPG-KEY-EUGridPMA-RPM-3
EOF

yum install -y vim
yum install -y nano
yum groupinstall -y 'Development Tools'
yum install -y epel-release yum-builddep git
yum-builddep -y "/vagrant/packaging/rpm/fts-rest.spec"
yum install -y gfal2-all httpd mod_ssl mod_gridsite voms-config-vo-dteam ca-policy-egi-core MySQL-python
yum install -y `grep  '^Requires' /vagrant/packaging/rpm/fts-rest.spec  | awk '{print $2}' | grep -oE "^[[:alnum:]\._-]+" | grep -v fts`

# Configure Apache
useradd "fts3"

mkdir -p "/etc/fts3"
cp "/vagrant/src/fts3rest/fts3config.test" "/etc/fts3/fts3config"
cp "/vagrant/src/fts3rest/fts3rest.ini" "/etc/fts3/fts3rest.ini"

rm -fv "/etc/httpd/conf.d/ssl.conf"
cp "/vagrant/src/fts3rest/fts3rest.conf" "/etc/httpd/conf.d"

sed 's?WSGIDaemon.*?WSGIDaemonProcess fts3rest processes=2 threads=15 maximum-requests=3000 display-name=fts3rest user=fts3 group=fts3 python-path="/vagrant/src/fts3rest/:/vagrant/src/"?g' /etc/httpd/conf.d/fts3rest.conf -i
sed "s:/usr/libexec/fts3/fts3rest.wsgi:/vagrant/src/fts3rest/fts3rest.wsgi:g" /etc/httpd/conf.d/fts3rest.conf -i

mkdir -p "/var/log/fts3rest/"
mkdir -p "/var/lib/fts3/"
chown fts3.fts3 "/var/log/fts3rest/"
chown fts3.fts3 "/var/lib/fts3/"

# Disable selinux
setenforce 0
sed "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config -i

# Need a self-signed certificate, which can be replaced later on
if [[ ! -f "/etc/grid-security/hostcert.pem" ]]; then
    openssl req -x509 -newkey rsa:2048 -keyout "/etc/grid-security/hostkey.pem" -out "/etc/grid-security/hostcert.pem" -days 365 -nodes -subj '/CN=self-signed-rest'
    chmod 0400 "/etc/grid-security/hostkey.pem"
fi

# Start apache
systemctl enable httpd
systemctl start httpd

