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
# correct inerpreter
%global __os_install_post %__multiple_python_os_install_post
%endif

Name:			fts-rest
Version:		0.0.1
Release:		9
BuildArch:		noarch
Summary:		FTS3 Rest Interface
Group:			Applications/Internet
License:		ASL 2.0
URL:			https://svnweb.cern.ch/trac/fts3
Source0:		%{name}-%{version}.tar.gz
Buildroot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	cmake
%if 0%{?with_python26}
BuildRequires:	python26-devel
%else
BuildRequires:	python-devel
%endif

Requires:		gridsite%{?_isa} >= 1.7
Requires:		httpd%{?_isa}
Requires:		mod_wsgi
Requires:		python-fts
Requires:		python-paste-deploy
Requires:		python-pylons

%description
This package provides the FTS3 REST interface

%package cli
Summary:		FTS3 Rest Interface CLI
Group:			Applications/Internet

Requires:		python-fts

%description cli
Command line utilities for the FTS3 REST interface

%package selinux
Summary:		SELinux support for fts-rest
Group:			Applications/Internet

Requires:		fts-rest

%description selinux
This package labels port 8446, used by fts-rest, as http_port_t,
so Apache can bind to it.

%post selinux
if [ "$1" -le "1" ] ; then # First install
semanage port -a -t http_port_t -p tcp 8446
fi

%preun selinux
if [ "$1" -lt "1" ] ; then # Final removal
semanage port -d -t http_port_t -p tcp 8446
fi

%prep
%setup -q -n %{name}-%{version}

%build
%cmake . -DCMAKE_INSTALL_PREFIX=/
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
make install DESTDIR=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitearch}/*
%{_libexecdir}/fts3
%config(noreplace) %{_sysconfdir}/fts3/fts3rest.ini
%config(noreplace) %{_sysconfdir}/httpd/conf.d/fts3rest.conf

%files cli
%defattr(-,root,root,-)
%{_bindir}/fts-rest-*
%config(noreplace) %{_sysconfdir}/fts3/fts3client.cfg

%files selinux

%changelog
* Tue Jul 02 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.1-9
- Introduced -selinux package

* Thu Mar 21 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.1-1
- Initial build

