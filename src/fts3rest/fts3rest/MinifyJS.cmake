function (Minify SLIMIT JSROOT)

    message (STATUS "Trying to minimize files under ${JSROOT}")

    file (GLOB_RECURSE JSFILES
        "${JSROOT}/*.js"
    )

    foreach (JS ${JSFILES})
        message ("Minimizing ${JS}")
        execute_process (
            COMMAND "${SLIMIT}" -m "${JS}"
            OUTPUT_VARIABLE MINJS
        )
        file(WRITE "${JS}" "${MINJS}")
    endforeach (JS)

endfunction (Minify)
