#!/bin/bash
this_script=`readlink -f "$0"`
this_dir=`dirname "$this_script"`

version=`sed -nre 's/^Version:\s+((([0-9]+)\.)*[0-9]+)/\1/p' "${this_dir}/dist/fts-rest.spec"`

echo "Packaging version $version"
mkdir -p /tmp/fts-rest/SOURCES/
cd "$this_dir" > /dev/null
tar czf /tmp/fts-rest/SOURCES/fts-rest-$version.tar.gz . --exclude=.git --exclude="*.pyc"
cd - > /dev/null

rpmbuild -bs "${this_dir}/dist/fts-rest.spec" \
    --define='_topdir /tmp/fts-rest/' \
    --define='_sourcedir %{_topdir}/SOURCES' \
    --define='_builddir %{_topdir}/BUILD' \
    --define='_srcrpmdir %{_topdir}/SRPMS' \
    --define='_rpmdir %{_topdir}/RPMS' > /dev/null

cp /tmp/fts-rest/SRPMS/*.rpm .
rm -rf /tmp/fts-rest/
