#!/bin/bash

# Were are we?
SOURCE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo "Script located at ${SOURCE_DIR}"

# Locations
VIRTUALENV="/tmp/qa-env"
COVERAGE_XML="${SOURCE_DIR}/coverage.xml"
NOSETESTS_XML="${SOURCE_DIR}/nosetests.xml"

# Setup virtualenv
if [ ! -e "${VIRTUALENV}" ]; then
    echo "Creating ${VIRTUALENV}"
    virtualenv "${VIRTUALENV}"
    if [ $? -ne 0 ]; then
        echo "virtualenv failed"
        exit 1
    fi
else
    echo "${VIRTUALENV} already exists"
fi

echo "Activating"
. "${VIRTUALENV}/bin/activate"


# Install dependencies
echo "Installing dependencies"
pip install --upgrade WebTest==1.4.3 WebOb==1.1.1 Pylons==1.0, nose==1.2 nose-cov==1.2 sqlalchemy M2Crypto m2ext python-dateutil requests jsonschema
if [ $? -ne 0 ]; then
    echo "pip install failed"
    exit 1
fi

# Run the tests
echo "Running the tests"

export PYTHONPATH=$PYTHONPATH:${SOURCE_DIR}/..

nosetests --with-coverage --cover-xml --cover-xml-file="${COVERAGE_XML}" --with-xunit --xunit-file="${NOSETESTS_XML}" --cover-package="fts3rest"

# Ready to go!
if [ -e "${COVERAGE_XML}" ] && [ -e "${NOSETESTS_XML}" ]; then
    echo "Ready to run sonar-runner"
else
    echo "Reports not found"
fi
