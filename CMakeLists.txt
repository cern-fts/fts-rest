cmake_minimum_required (VERSION 2.6)

project (fts3-misc)

# Python libraries location
execute_process (COMMAND python -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)"
                 OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
                 OUTPUT_STRIP_TRAILING_WHITESPACE)

# Subdirectories
add_subdirectory (src)
