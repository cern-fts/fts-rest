cmake_minimum_required (VERSION 2.6)

# man pages
set(MAN_INPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/man/")

add_custom_target(md_documentation
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/generate-cli-md.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)

add_custom_target(man_pages ALL)

file(GLOB md_files "${CMAKE_CURRENT_SOURCE_DIR}/cli/*.md")
foreach(md ${md_files})
    get_filename_component(man_name "${md}" NAME_WE)
    add_custom_target(
        "${man_name}.1"
        COMMAND pandoc -s -t man "${md}" -o "${CMAKE_CURRENT_SOURCE_DIR}/man/${man_name}.1"
    )
    add_dependencies(man_pages "${man_name}.1")
endforeach()

if (NOT SHARE_INSTALL_PREFIX)
    set (SHARE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}/share")
endif (NOT SHARE_INSTALL_PREFIX)

install(DIRECTORY
            "${MAN_INPUT_DIR}"
        DESTINATION
            "${SHARE_INSTALL_PREFIX}/man/man1/"
        FILES_MATCHING PATTERN fts-rest-*.1
)
