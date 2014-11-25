%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}

Name:           fts-rest
Version:        3.2.31
Release:        1%{?dist}
BuildArch:      noarch
Summary:        FTS3 Rest Interface
Group:          Applications/Internet
License:        ASL 2.0
URL:            https://svnweb.cern.ch/trac/fts3
Source0:        https://grid-deployment.web.cern.ch/grid-deployment/dms/fts3/tar/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  python-jsonschema
%if %{?rhel}%{!?rhel:0} == 6
BuildRequires:  python-nose1.1
%endif
%if %{?rhel}%{!?rhel:0} >= 7
BuildRequires:  python-nose
%endif
BuildRequires:  python-pylons
BuildRequires:  scipy
BuildRequires:  m2crypto
BuildRequires:  python-coverage
BuildRequires:  python-sqlalchemy
BuildRequires:  python-requests
BuildRequires:  python-dateutil
BuildRequires:  pandoc

Requires:     gridsite%{?_isa} >= 1.7
Requires:     httpd%{?_isa}
Requires:     mod_wsgi
Requires:     python-fts = %{version}-%{release}
Requires:     python-paste-deploy
Requires:     python-dateutil
Requires:     python-pylons
Requires:     gfal2-python

%description
This package provides the FTS3 REST interface

%package cloud-storage
Summary:        FTS3 Rest Cloud Storage extensions
Group:          Applications/Internet

Requires:       fts-rest = %{version}-%{release}

%description cloud-storage
FTS3 Rest Cloud Storage extensions. Includes support for Dropbox

%package oauth2
Summary:        FTS3 Rest OAuth2 provider
Group:          Applications/Internet

Requires:       fts-rest = %{version}-%{release}

%description oauth2
FTS3 Rest OAuth2 provider

%package cli
Summary:        FTS3 Rest Interface CLI
Group:          Applications/Internet

Requires:       python-fts = %{version}-%{release}

%description cli
Command line utilities for the FTS3 REST interface

%package selinux
Summary:        SELinux support for fts-rest
Group:          Applications/Internet

Requires:       %{name} = %{version}-%{release}

%description selinux
SELinux support for fts-rest

%package -n python-fts
Summary:        FTS3 database model
Group:          Applications/Internet
Requires:       m2crypto
Requires:       python-pycurl
Requires:       python-sqlalchemy

%description -n python-fts
This package provides an object model of the FTS3
database, using sqlalchemy ORM.

%post
/sbin/service httpd condrestart >/dev/null 2>&1 || :

%postun
if [ "$1" -eq "0" ] ; then
    /sbin/service httpd condrestart >/dev/null 2>&1 || :
fi

%post selinux
if [ "$1" -le "1" ] ; then # First install
semanage port -a -t http_port_t -p tcp 8446
setsebool -P httpd_can_network_connect=1
setsebool -P httpd_setrlimit=1
semanage fcontext -a -t httpd_log_t "/var/log/fts3rest(/.*)?"
restorecon -R /var/log/fts3rest/
fi

%preun selinux
if [ "$1" -lt "1" ] ; then # Final removal
semanage port -d -t http_port_t -p tcp 8446
setsebool -P httpd_can_network_connect=0
setsebool -P httpd_setrlimit=0
fi

%prep
%setup -qc

%build
%cmake . -DCMAKE_INSTALL_PREFIX=/ -DPYTHON_SITE_PACKAGES=%{python_sitelib}
make %{?_smp_mflags}

%check
pushd src/fts3rest
%if %{?rhel}%{!?rhel:0} == 6
PYTHONPATH=../ nosetests1.1 --with-xunit --xunit-file=/tmp/nosetests.xml
%endif
%if %{?rhel}%{!?rhel:0} >= 7
PYTHONPATH=../ ./setup_pylons_plugin.py install --user 
PYTHONPATH=../ nosetests --with-xunit --xunit-file=/tmp/nosetests.xml
%endif
popd

%install
mkdir -p %{buildroot}
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}/%{_var}/cache/fts3rest/
mkdir -p %{buildroot}/%{_var}/log/fts3rest/

cp --preserve=timestamps -r src/fts3 %{buildroot}/%{python_sitelib}

%files
%dir %{python_sitelib}/fts3rest/

%{python_sitelib}/fts3rest.egg-info/*

%{python_sitelib}/fts3rest/__init__.py*
%{python_sitelib}/fts3rest/websetup.py*

%{python_sitelib}/fts3rest/config/*.py*
%{python_sitelib}/fts3rest/config/routing/__init__.py*
%{python_sitelib}/fts3rest/config/routing/base.py*

%{python_sitelib}/fts3rest/controllers/api.py*
%{python_sitelib}/fts3rest/controllers/archive.py*
%{python_sitelib}/fts3rest/controllers/banning.py*
%{python_sitelib}/fts3rest/controllers/config.py*
%{python_sitelib}/fts3rest/controllers/datamanagement.py*
%{python_sitelib}/fts3rest/controllers/delegation.py*
%{python_sitelib}/fts3rest/controllers/error.py*
%{python_sitelib}/fts3rest/controllers/__init__.py*
%{python_sitelib}/fts3rest/controllers/jobs.py*
%{python_sitelib}/fts3rest/controllers/misc.py*
%{python_sitelib}/fts3rest/controllers/optimizer.py*
%{python_sitelib}/fts3rest/controllers/snapshot.py*

%{python_sitelib}/fts3rest/lib/api/
%{python_sitelib}/fts3rest/lib/app_globals.py*
%{python_sitelib}/fts3rest/lib/base.py*
%{python_sitelib}/fts3rest/lib/gfal2_wrapper.py*
%{python_sitelib}/fts3rest/lib/helpers/
%{python_sitelib}/fts3rest/lib/http_exceptions.py*
%{python_sitelib}/fts3rest/lib/__init__.py*
%{python_sitelib}/fts3rest/lib/middleware/*.py*
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/*.py*
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/methods/__init__.py*
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/methods/ssl.py*

%{python_sitelib}/fts3rest/model/

%{python_sitelib}/fts3rest/public/
%{python_sitelib}/fts3rest/templates/delegation.html

%{_libexecdir}/fts3
%config(noreplace) %{_sysconfdir}/fts3/fts3rest.ini
%config(noreplace) %{_sysconfdir}/httpd/conf.d/fts3rest.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/fts-rest
%dir %attr(0755,apache,apache) %{_var}/cache/fts3rest
%dir %attr(0755,apache,apache) %{_var}/log/fts3rest
%doc docs/README.md
%doc docs/install.md
%doc docs/api.md

%files cloud-storage
%{python_sitelib}/fts3rest/config/routing/cstorage.py*
%{python_sitelib}/fts3rest/controllers/cloudStorage.py*
%{python_sitelib}/fts3rest/controllers/CSdropbox.py*
%{python_sitelib}/fts3rest/controllers/CSInterface.py*

%files oauth2
%{python_sitelib}/fts3rest/config/routing/oauth2.py*
%{python_sitelib}/fts3rest/controllers/oauth2.py*
%{python_sitelib}/fts3rest/lib/oauth2lib/
%{python_sitelib}/fts3rest/lib/oauth2provider.py*
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/methods/oauth2.py*
%{python_sitelib}/fts3rest/templates/app.html
%{python_sitelib}/fts3rest/templates/apps.html
%{python_sitelib}/fts3rest/templates/authz_confirm.html
%{python_sitelib}/fts3rest/templates/authz_failure.html
%{python_sitelib}/fts3rest/templates/register.html

%files cli
%{_bindir}/fts-rest-*
%config(noreplace) %{_sysconfdir}/fts3/fts3client.cfg
%{_mandir}/man1/fts-rest*

%files selinux

%files -n python-fts
%{python_sitelib}/fts3
%doc LICENSE

%changelog
* Fri Aug 15 2014 Alejandro Álvarez <aalvarez@cern.ch> - 3.2.27-1
- Package separately oauth2 and cloud storage support

* Mon Jun 30 2014 Michal Simon <michal.simon@cern.ch> - 3.2.6-1
- First EPEL release

* Tue May 13 2014 Michal Simon <michal.simon@cern.ch> - 3.2.5-1
- Marging fts-rest and python-fts

* Mon Mar 10 2014 Alejandro Álvarez <aalvarez@cern.ch> - 3.2.0-1
- Creating log directory

* Fri Jan 03 2014 Alejandro Álvarez <aalvarez@cern.ch> - 3.1.0-1
- Major and minor versions follow FTS3

* Tue Aug 13 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.2-2
- Packaging /var/cache/fts3rest

* Tue Jul 02 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.1-9
- Introduced -selinux package

* Thu Mar 21 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.1-1
- Initial build
