cmake_minimum_required (VERSION 2.6)

# man pages

set(MAN_INPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/man/")

install(DIRECTORY
            "${MAN_INPUT_DIR}"
        DESTINATION
            "${SHARE_INSTALL_PREFIX}/man/man1/"
        FILES_MATCHING PATTERN "fts-rest-*.1"
)
