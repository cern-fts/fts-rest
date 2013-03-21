cmake_minimum_required (VERSION 2.6)

install (FILES         __init__.py websetup.py
         DESTINATION   ${PYTHON_SITE_PACKAGES}/fts3rest/
)

install (DIRECTORY   config
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
         PATTERN     "*.pyc" EXCLUDE
)

install (DIRECTORY   controllers
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
         PATTERN     "*.pyc" EXCLUDE
)

install (DIRECTORY   lib
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
         PATTERN     "*.pyc" EXCLUDE
)

install (DIRECTORY   model
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
         PATTERN     "*.pyc" EXCLUDE
)
