cmake_minimum_required (VERSION 2.6)

add_subdirectory (fts3rest)

# egg-info
install (DIRECTORY      fts3rest.egg-info
         DESTINATION    ${PYTHON_SITE_PACKAGES})

# WSGI
install (FILES          fts3rest.wsgi
         DESTINATION    usr/libexec/fts3/
)

# Configuration file
install (FILES          fts3rest.ini
         DESTINATION    etc/fts3
)

# Apache configuration file
install (FILES          fts3rest.conf
         DESTINATION    etc/httpd/conf.d
)
