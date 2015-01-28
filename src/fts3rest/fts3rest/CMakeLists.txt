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
         USE_SOURCE_PERMISSIONS
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
         PATTERN     "*.pyc" EXCLUDE
)

install (DIRECTORY   model
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
         PATTERN     "*.pyc" EXCLUDE
)

install (DIRECTORY templates
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
)

install (DIRECTORY public
         DESTINATION ${PYTHON_SITE_PACKAGES}/fts3rest
)

# Minify Javascript
find_program (SLIMIT slimit)
if (SLIMIT)
    message (STATUS "Found slimit: ${SLIMIT}")
    install(SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/MinifyJS.cmake"
        CODE "MINIFY(\"${SLIMIT}\" \"\$ENV{DESTDIR}/${PYTHON_SITE_PACKAGES}/fts3rest/public/js\")"
    )
endif (SLIMIT)
