cmake_minimum_required (VERSION 2.6)

install(PROGRAMS      fts-rest-transfer-cancel
                      fts-rest-transfer-list
                      fts-rest-transfer-status
                      fts-rest-transfer-submit
                      fts-rest-delegate
        DESTINATION   usr/bin
)
