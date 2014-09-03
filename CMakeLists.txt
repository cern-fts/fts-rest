cmake_minimum_required (VERSION 2.6)

project (fts-rest)

# Python libraries location
if (NOT DEFINED PYTHON_SITE_PACKAGES)
    execute_process (COMMAND python -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)"
                     OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
                     OUTPUT_STRIP_TRAILING_WHITESPACE)
endif (NOT DEFINED PYTHON_SITE_PACKAGES)

# Subdirectories
add_subdirectory (src)
add_subdirectory (docs)
