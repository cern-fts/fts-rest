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
