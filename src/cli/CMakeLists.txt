cmake_minimum_required (VERSION 2.6)

install(PROGRAMS      fts-rest-transfer-cancel
                      fts-rest-transfer-list
                      fts-rest-transfer-status
                      fts-rest-transfer-submit
                      fts-rest-delegate
                      fts-rest-whoami
        DESTINATION   usr/bin
)

# Configuration file
install (FILES          fts3client.cfg
         DESTINATION    etc/fts3
)

# man pages

set(MAN_INPUT_DIR "${PROJECT_SOURCE_DIR}/docs/man/")
 
install(FILES 
            "${MAN_INPUT_DIR}/fts-rest-transfer-cancel.1"
            "${MAN_INPUT_DIR}/fts-rest-transfer-list.1"
            "${MAN_INPUT_DIR}/fts-rest-transfer-status.1"
            "${MAN_INPUT_DIR}/fts-rest-transfer-submit.1"
            "${MAN_INPUT_DIR}/fts-rest-delegate.1"
            "${MAN_INPUT_DIR}/fts-rest-whoami.1"
        DESTINATION 
            "${SHARE_INSTALL_PREFIX}/man/man1/"
)

 

