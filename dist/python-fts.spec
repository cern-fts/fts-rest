%if 0%{?rhel} == 5
%global with_python26 1
%endif

%if 0%{?with_python26}
%global __python %{_bindir}/python2.6
%global __os_install_post %{?__python26_os_install_post}
%endif

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib(1))")}

Name:			python-fts
Version:		3.2.3
Release:		1
BuildArch:		noarch
Summary:		FTS3 database model
Group:			Applications/Internet
License:		ASL 2.0
URL:			https://svnweb.cern.ch/trac/fts3
Source0:		%{name}-%{version}.tar.gz
Buildroot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if 0%{?with_python26}
BuildRequires:	python26-devel
Requires:		python26-m2crypto
Requires:       python26-pycurl
Requires:		python26-sqlalchemy
%else
Requires:		m2crypto
BuildRequires:	python-devel
Requires:       python-pycurl
Requires:		python-sqlalchemy
%endif

%description
This package provides an object model of the FTS3
database, using sqlalchemy ORM.

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{python_sitearch}
cp --preserve=timestamps -r src/fts3 %{buildroot}/%{python_sitearch}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitearch}/*

%changelog
* Mon Apr 14 2014 Alejandro Álvarez <aalvarez@cern.ch> - 3.2.2-1
- Adapted for EL5

* Mon Jan 03 2014 Alejandro Álvarez <aalvarez@cern.ch> - 3.1.0-1
- Major and minor versions follow FTS3

* Thu Mar 21 2013 Alejandro Álvarez <aalvarez@cern.ch> - 0.0.1-1
- Initial build

