%if 0%{?rhel} == 5
%global with_python26 1
%endif

%if 0%{?with_python26}
%global __python %{_bindir}/python2.6
%global __os_install_post %{?__python26_os_install_post}
%endif

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}

Name:           fts-rest
Version:        3.2.5
Release:        1
BuildArch:      noarch
Summary:        FTS3 Rest Interface
Group:          Applications/Internet
License:        ASL 2.0
URL:            https://svnweb.cern.ch/trac/fts3
Source0:        https://grid-deployment.web.cern.ch/grid-deployment/dms/fts3/tar/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  python2-devel

%if 0%{?rhel} > 5
BuildRequires:  python-jsonschema
BuildRequires:  python-nose1.1
BuildRequires:  python-pylons
BuildRequires:  scipy
%endif

%if 0%{?with_python26}
BuildRequires:  python26-m2crypto
BuildRequires:  python26-sqlalchemy
%else
BuildRequires:  m2crypto
BuildRequires:  python-sqlalchemy
%endif

Requires:     gridsite%{?_isa} >= 1.7
Requires:     httpd%{?_isa}
Requires:     mod_wsgi
Requires:     python-fts = %{version}-%{release}
Requires:     python-paste-deploy
Requires:     python-pylons
Requires:     gfal2-python

%description
This package provides the FTS3 REST interface

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
This package labels port 8446, used by fts-rest, as http_port_t,
so Apache can bind to it.

%package -n python-fts
Summary:        FTS3 database model
Group:          Applications/Internet

%if 0%{?with_python26}
BuildRequires:  python26-devel
Requires:       python26-m2crypto
Requires:       python26-pycurl
Requires:       python26-sqlalchemy
%else
Requires:       m2crypto
BuildRequires:  python-devel
Requires:       python-pycurl
Requires:       python-sqlalchemy
%endif

%description -n python-fts
This package provides an object model of the FTS3
database, using sqlalchemy ORM.

%post selinux
if [ "$1" -le "1" ] ; then # First install
semanage port -a -t http_port_t -p tcp 8446
setsebool -P httpd_can_network_connect=1
setsebool -P httpd_setrlimit=1
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

# In EL5, use Python2.6
%if 0%{?with_python26}
sed -i 's:#!/usr/bin/env python:#!/usr/bin/env python26:g' src/cli/fts-rest-*
%endif

%check
%if 0%{?rhel} > 5
pushd src/fts3rest
PYTHONPATH=../ nosetests1.1 --with-xunit --xunit-file=/tmp/nosetests.xml
popd
%endif

%install
mkdir -p %{buildroot}
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}/%{_var}/cache/fts3rest/
mkdir -p %{buildroot}/%{_var}/log/fts3rest/

cp --preserve=timestamps -r src/fts3 %{buildroot}/%{python_sitelib}

%files
%{python_sitelib}/fts3rest*
%{_libexecdir}/fts3
%dir %config(noreplace) %{_sysconfdir}/fts3
%config(noreplace) %{_sysconfdir}/fts3/fts3rest.ini
%config(noreplace) %{_sysconfdir}/httpd/conf.d/fts3rest.conf
%dir %attr(0755,apache,apache) %{_var}/cache/fts3rest
%dir %attr(0755,apache,apache) %{_var}/log/fts3rest
%doc docs/README.md
%doc docs/install.md
%doc docs/api.md

%files cli
%{_bindir}/fts-rest-*
%dir %config(noreplace) %{_sysconfdir}/fts3
%config(noreplace) %{_sysconfdir}/fts3/fts3client.cfg
%{_mandir}/man1/fts-rest*

%files selinux

%files -n python-fts
%{python_sitelib}/fts3
%doc LICENSE

%changelog
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
