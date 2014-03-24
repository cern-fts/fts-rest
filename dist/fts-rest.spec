%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}

%if 0%{?rhel} == 5
%global with_python26 1
%endif

%if 0%{?with_python26}
%global __python26 %{_bindir}/python2.6
%global py26dir %{_builddir}/python26-%{name}-%{version}-%{release}
%{!?python26_sitelib: %global python26_sitelib %(%{__python26} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python26_sitearch: %global python26_sitearch %(%{__python26} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}
# Update rpm byte compilation script so that we get the modules compiled by the
# correct interpreter
%global __os_install_post %__multiple_python_os_install_post
%endif

Name:           fts-rest
Version:        3.2.0
Release:        1
BuildArch:      noarch
Summary:        FTS3 Rest Interface
Group:          Applications/Internet
License:        ASL 2.0
URL:            https://svnweb.cern.ch/trac/fts3
Source0:        %{name}-%{version}.tar.gz
Buildroot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  cmake
BuildRequires:  m2crypto
BuildRequires:  python-fts
BuildRequires:  python-jsonschema
BuildRequires:  python-nose
BuildRequires:  python-pylons
%if 0%{?with_python26}
BuildRequires:  python26-devel
%else
BuildRequires:  python-devel
%endif
BuildRequires:  scipy

Requires:     gridsite%{?_isa} >= 1.7
Requires:     httpd%{?_isa}
Requires:     m2crypto
Requires:     mod_wsgi
Requires:     python-fts
Requires:     python-paste-deploy
Requires:     python-pylons
Requires:     gfal2-python

%description
This package provides the FTS3 REST interface

%package cli
Summary:        FTS3 Rest Interface CLI
Group:          Applications/Internet

Requires:       python-fts
Requires:       python-pycurl

%description cli
Command line utilities for the FTS3 REST interface

%package selinux
Summary:        SELinux support for fts-rest
Group:          Applications/Internet

Requires:       fts-rest

%description selinux
This package labels port 8446, used by fts-rest, as http_port_t,
so Apache can bind to it.

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
%setup -q -n %{name}-%{version}

%build
%cmake . -DCMAKE_INSTALL_PREFIX=/
make %{?_smp_mflags}

%check
pushd src/fts3rest
nosetests -x
popd

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}/%{_var}/cache/fts3rest/
mkdir -p %{buildroot}/%{_var}/log/fts3rest/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitearch}/*
%{_libexecdir}/fts3
%config(noreplace) %{_sysconfdir}/fts3/fts3rest.ini
%config(noreplace) %{_sysconfdir}/httpd/conf.d/fts3rest.conf
%dir %attr(0775,apache,apache) %{_var}/cache/fts3rest
%dir %attr(0775,apache,apache) %{_var}/log/fts3rest

%files cli
%defattr(-,root,root,-)
%{_bindir}/fts-rest-*
%config(noreplace) %{_sysconfdir}/fts3/fts3client.cfg

%files selinux

%changelog
* Mon Mar 10 2014 Alejandro Álvarez <aalvarez@cern.ch> - 3.2.0-1
- Creating log directory

* Mon Jan 03 2014 Alejandro Álvarez <aalvarez@cern.ch> - 3.1.0-1
- Major and minor versions follow FTS3

* Tue Aug 13 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.2-2
- Packaging /var/cache/fts3rest

* Tue Jul 02 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.1-9
- Introduced -selinux package

* Thu Mar 21 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.1-1
- Initial build

