%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}

%{!?nosetest_path: %global nosetest_path "/tmp"}

Name:           fts-rest
Version:        3.11.1
Release:        1%{?dist}
BuildArch:      noarch
Summary:        FTS3 Rest Interface
Group:          Applications/Internet
License:        ASL 2.0
URL:            https://fts.web.cern.ch/
# The source for this package was pulled from upstream VCS.
# Use the following commands to generate the tarball:
# git clone https://gitlab.cern.ch/fts/fts-rest.git -b master --depth 1 fts-rest-3.11.0
# cd fts-rest-3.11.0
# git checkout v3.11.0
# git submodule init && git submodule update
# cd ..
# tar -vczf fts-rest-3.11.0.tar.gz --exclude-vcs fts-rest-3.11.0
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gfal2-python
BuildRequires:  gfal2-plugin-mock
BuildRequires:  cmake
BuildRequires:  python-jsonschema
%if %{?rhel}%{!?rhel:0} == 6
BuildRequires:  python-nose1.1
%endif
%if %{?rhel}%{!?rhel:0} >= 7
BuildRequires:  python-nose
%endif

BuildRequires:  python-dateutil
BuildRequires:  python-pylons
BuildRequires:  scipy
BuildRequires:  m2crypto
BuildRequires:  python-mock
BuildRequires:  python-m2ext
%if %{?rhel}%{!?rhel:0} >= 7
BuildRequires:  python-sqlalchemy
%else
BuildRequires:  python-sqlalchemy0.8
%endif
BuildRequires:  python-requests
BuildRequires:  python-urllib3
%if %{?rhel}%{!?rhel:0} == 6
BuildRequires:  python-slimit
%endif
BuildRequires:  pandoc
BuildRequires:  python-dirq
BuildRequires:  python-pycurl
BuildRequires:  MySQL-python

BuildRequires:  python-jwcrypto
BuildRequires:  python-jwt
BuildRequires:  python-oic


Requires:       gridsite%{?_isa} >= 1.7
%if %{?rhel}%{!?rhel:0} == 6
Requires:       httpd%{?_isa} >= 2.2.15-60
%endif
%if %{?rhel}%{!?rhel:0} >= 7
Requires:       httpd%{?_isa}
%endif
Requires:       python-oic
Requires:       python-jwcrypto >= 0.6
Requires:       python-jwt
Requires:       mod_wsgi
Requires:       python-dirq
Requires:       python-fts = %{version}-%{release}
Requires:       python-paste-deploy
Requires:       python-pylons
Requires:       python-simplejson%{?_isa}
Requires:       gfal2-python%{?_isa}
Requires:       python-requests
Requires:       python-urllib3


%description
This package provides the FTS3 REST interface

%if %{?rhel}%{!?rhel:0} >= 7
%package firewalld
Summary: FTS3 Rest Firewalld
Group: Applications/Internet

Requires:  firewalld-filesystem

%description firewalld
FTS3 Rest firewalld.
%endif

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

%package http-authz-signed-cert
Summary:        FTS3 Rest HTTP_AUTHORIZATION signed-cert method
Group:          Application/Internet

Requires:       python-dateutil
Requires:       python-m2ext
Requires:       fts-rest = %{version}-%{release}

%description http-authz-signed-cert
FTS3 Rest HTTP_AUTHORIZATION signed-cert method

%package cli
Summary:        FTS3 Rest Interface CLI
Group:          Applications/Internet

Requires:       python-fts = %{version}-%{release}
Requires:       python-m2ext

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
%if %{?rhel}%{!?rhel:0} >= 7
Requires:       python-sqlalchemy
%else
Requires:       python-sqlalchemy0.8
%endif
Requires:       python-requests
#Requires:       python-requests >= 2.23
#Requires:       python-chardet >= 3.0.2
#Requires:       python-idna >= 2.5
#Requires:       python-urllib3 >= 1.21.1
#Requires:       python-certifi >= 2017.4.17

%description -n python-fts
This package provides an object model of the FTS3
database, using sqlalchemy ORM.


%post
/sbin/service httpd condrestart >/dev/null 2>&1 || :
if [ "$1" -eq "2" ]; then # Upgrade
    # 3.5.1 needs owner to be fts3, since fts3rest runs as fts3
    chown fts3.fts3 /var/log/fts3rest
    chown fts3.fts3 /var/log/fts3rest/fts3rest.log || true
fi

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
%setup -q

%build
# Make sure the version in the spec file and the version used
# for building matches
fts_api_ver=`awk 'match($0, /^API_VERSION = dict\(major=([0-9]+), minor=([0-9]+), patch=([0-9]+)\)/, m) {print m[1]"."m[2]"."m[3]; }' src/fts3rest/fts3rest/controllers/api.py`
fts_spec_ver=`expr "%{version}" : '\([0-9]*\\.[0-9]*\\.[0-9]*\)'`
if [ "$fts_api_ver" != "$fts_spec_ver" ]; then
    echo "The version in the spec file does not match the api.py version!"
    echo "$fts_api_ver != %{version}"
    exit 1
fi

%cmake . -DCMAKE_INSTALL_PREFIX=/ -DPYTHON_SITE_PACKAGES=%{python_sitelib}

make %{?_smp_mflags}

%check
pushd src/fts3rest
%if %{?rhel}%{!?rhel:0} == 6
PYTHONPATH=../:/usr/lib64/python2.6/site-packages/SQLAlchemy-0.8.2-py2.6-linux-x86_64.egg/ \
    nosetests1.1 --with-xunit --xunit-file=%{?nosetest_path}/nosetests.xml --no-skip
%endif
%if %{?rhel}%{!?rhel:0} >= 7
PYTHONPATH=../ ./setup_pylons_plugin.py install --user
PYTHONPATH=../ nosetests --with-xunit --xunit-file=%{?nosetest_path}/nosetests.xml --no-skip
%endif
popd

%install
mkdir -p %{buildroot}
make install DESTDIR=%{buildroot}
%if %{?rhel}%{!?rhel:0} == 6
rm -rf %{buildroot}/%{_prefix}/lib/firewalld/services/fts3rest.xml
%endif
mkdir -p %{buildroot}/%{_var}/cache/fts3rest/
mkdir -p %{buildroot}/%{_var}/log/fts3rest/


cp --preserve=timestamps -r src/fts3 %{buildroot}/%{python_sitelib}
cat > %{buildroot}/%{python_sitelib}/fts3.egg-info <<EOF
Metadata-Version: 1.0
Name: fts3
Version: %{version}
Summary: FTS3 Python Libraries.
Home-page: http://fts3-service.web.cern.ch
Author: FTS Developers
Author-email: fts-devel@cern.ch
License: Apache2
EOF

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
%{python_sitelib}/fts3rest/controllers/autocomplete.py*
%{python_sitelib}/fts3rest/controllers/banning.py*
%{python_sitelib}/fts3rest/controllers/config/*.py*
%{python_sitelib}/fts3rest/controllers/datamanagement.py*
%{python_sitelib}/fts3rest/controllers/delegation.py*
%{python_sitelib}/fts3rest/controllers/error.py*
%{python_sitelib}/fts3rest/controllers/__init__.py*
%{python_sitelib}/fts3rest/controllers/files.py*
%{python_sitelib}/fts3rest/controllers/jobs.py*
%{python_sitelib}/fts3rest/controllers/optimizer.py*
%{python_sitelib}/fts3rest/controllers/serverstatus.py*

%{python_sitelib}/fts3rest/lib/api/
%{python_sitelib}/fts3rest/lib/app_globals.py*
%{python_sitelib}/fts3rest/lib/base.py*
%{python_sitelib}/fts3rest/lib/openidconnect.py*
%{python_sitelib}/fts3rest/lib/gfal2_wrapper.py*
%{python_sitelib}/fts3rest/lib/heartbeat.py*
%{python_sitelib}/fts3rest/lib/IAMTokenRefresher.py*
%{python_sitelib}/fts3rest/lib/helpers/
%{python_sitelib}/fts3rest/lib/http_exceptions.py*
%{python_sitelib}/fts3rest/lib/__init__.py*
%{python_sitelib}/fts3rest/lib/JobBuilder.py*
%{python_sitelib}/fts3rest/lib/middleware/*.py*
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/*.py*
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/methods/__init__.py*
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/methods/ssl.py*
%{python_sitelib}/fts3rest/lib/scheduler/schd.py*
%{python_sitelib}/fts3rest/lib/scheduler/db.py*
%{python_sitelib}/fts3rest/lib/scheduler/Cache.py*
%{python_sitelib}/fts3rest/lib/scheduler/__init__.py*

%{python_sitelib}/fts3rest/model/

%{python_sitelib}/fts3rest/public/
%{python_sitelib}/fts3rest/templates/delegation.html
%{python_sitelib}/fts3rest/templates/config/

%{_libexecdir}/fts3
%config(noreplace) %{_sysconfdir}/fts3/fts3rest.ini
%config(noreplace) %{_sysconfdir}/httpd/conf.d/fts3rest.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/fts-rest
%config(noreplace) %{_sysconfdir}/cron.d/fts-rest-graceful.cron
%dir %attr(0755,fts3,fts3) %{_var}/cache/fts3rest
%dir %attr(0755,fts3,fts3) %{_var}/log/fts3rest
%doc docs/README.md
%doc docs/install.md
%doc docs/api.md

%if %{?rhel}%{!?rhel:0} >= 7
%files firewalld
%config(noreplace) %{_prefix}/lib/firewalld/services/fts3rest.xml
%endif

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
%{python_sitelib}/fts3rest/templates/app_register.html
%{python_sitelib}/fts3rest/templates/apps.html
%{python_sitelib}/fts3rest/templates/authz_confirm.html
%{python_sitelib}/fts3rest/templates/authz_failure.html
%{python_sitelib}/fts3rest/templates/authz_noredirect.html

%files http-authz-signed-cert
%{python_sitelib}/fts3rest/lib/middleware/fts3auth/methods/http.py*

%files cli
%{_bindir}/fts-rest-*
%config(noreplace) %{_sysconfdir}/fts3/fts3client.cfg
%{_mandir}/man1/fts-rest*

%files selinux

%files -n python-fts
%{python_sitelib}/fts3
%{python_sitelib}/fts3.egg-info
%doc LICENSE



%changelog
* Wed Sep 22 2021 Mihai Patrascoiu <mihai.patrascoiu@cern.ch> - 3.11.0-1
- New Minor release
- Destination file report feature

* Fri Feb 12 2021 Mihai Patrascoiu <mihai.patrascoiu@cern.ch> - 3.10.1-1
- New bugfix release

* Mon Dec 07 2020 Mihai Patrascoiu <mihai.patrascoiu@cern.ch> - 3.10.0-1
- New Minor release
- OIDC Tokens Integration
- Archive Monitoring and QoS features

* Tue Jun 02 2020 Carles Garcia Cabot <carles.garcia.cabot@cern.ch> - 3.9.4-1
- New bugfix release

* Thu Nov 21 2019 Andrea Manzi <amanzi@cern.ch> - 3.9.3-1
- New bugfix release

* Mon Aug 19 2019 Andrea Manzi <amanzi@cern.ch> - 3.9.2-1
- New bugfix release

* Thu Feb 21 2019 Andrea Manzi <amanzi@cern.ch> - 3.8.3-1
- New bugfix release

* Thu Jan 10 2019 Andrea Manzi <amanzi@cern.ch> - 3.8.2-1
- New bugfix release

* Tue Oct 16 2018 Andrea Manzi <amanzi@cern.ch> - 3.8.1-1
- New bugfix release

* Mon Sep 24 2018 Andrea Manzi <amanzi@cern.ch> - 3.8.0-1
- New Minor release
- Initial support for Macaroons/Scitokens
- Multihop Scheduler merged into Standard Scheduling system
- AutoSessionReuse support

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Dec 17 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
- Python 2 binary package renamed to python2-fts
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.6.3-3
- Python 2 binary package renamed to python2-fts-rest
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Apr 18 2017 Alejandro Alvarez Ayllon <aalvarez@cern.ch> - 3.6.3-1
- Update for new upstream release

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Nov 15 2016 Alejandro Alvarez Ayllon <aalvarez@cern.ch> - 3.5.4-1
- Update for new upstream release

* Tue Apr 19 2016 Alejandro Alvarez Ayllon <aalvarez@cern.ch> - 3.4.0-1
- Update for new upstream release

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.32-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Mar 13 2015 Alejandro Alvarez Ayllon <aalvarez@cern.ch> - 3.2.32-2
- Missing dependencies

* Fri Mar 13 2015 Alejandro Alvarez Ayllon <aalvarez@cern.ch> - 3.2.32-1
- Update for new upstream release

* Fri Aug 15 2014 Michal Simon <michal.simon@cern.ch> - 3.2.26-2
- Update for new upstream release

* Mon Jun 30 2014 Michal Simon <michal.simon@cern.ch> - 3.2.26-1
- First EPEL release

* Tue May 13 2014 Michal Simon <michal.simon@cern.ch> - 3.2.25-1
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
