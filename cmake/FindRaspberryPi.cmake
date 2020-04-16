function (CHECK_IS_RASPBERRY_PI IS_RPI MODEL)
    if (UNIX AND NOT APPLE)
        # https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md
        # Copied from
        # https://github.com/juj/fbcp-ili9341/blob/master/CMakeLists.txt
        # Detect if current hardware is Raspberry Pi Zero/Zero W
	#
        execute_process(COMMAND cat /proc/cpuinfo OUTPUT_VARIABLE CPU_INFO)
        STRING(REGEX MATCH "Revision[\t ]*:[\t ]*([0-9a-f]+)" BOARD_REVISION ${CPU_INFO})
        set(BOARD_REVISION "${CMAKE_MATCH_1}")
        message(STATUS "Board revision: ${CMAKE_MATCH_1}")
        # http://ozzmaker.com/check-raspberry-software-hardware-version-command-line/
        if (BOARD_REVISION MATCHES "(0002)|(0003)|(0004)|(0005)|(0006)|(0007)|(0008)|(0009)" OR BOARD_REVISION MATCHES "(000d)|(000e)|(000f)|(0010)|(0011)|(0012)" OR BOARD_REVISION MATCHES "(900092)|(900093)|(9000c1)")
	    message(STATUS "Detected this Pi to be one of: Pi A, A+, B rev. 1, B rev. 2, B+, CM1, Zero or Zero W, with single hardware core and ARMv6Z instruction set CPU.")
            set(${IS_RPI} 1 PARENT_SCOPE)
            set(${MODEL} "Raspberry Pi" PARENT_SCOPE)
        elseif(BOARD_REVISION MATCHES "(a01041)|(a21041)")
	    message(STATUS "Detected this board to be a Pi 2 Model B < rev 1.2 with ARMv7-A instruction set CPU.")
            set(${IS_RPI} 1 PARENT_SCOPE)
            set(${MODEL} "Raspberry Pi 2" PARENT_SCOPE)
        elseif(BOARD_REVISION MATCHES "(a02082)|(a22082)|(a020d3)|(9020e0)|(a03111)|(b03111)|(c03111)")
            message(STATUS "Detected this Pi to be one of: Pi 2B rev. 1.2, 3B, 3B+, 3A+, CM3, CM3 lite or 4B(1GB,2GB,4GB RAM), with 4 hardware cores and ARMv8-A instruction set CPU.")
            set(${IS_RPI} 1 PARENT_SCOPE)
            set(${MODEL} "Raspberry Pi 3 or 4" PARENT_SCOPE)
        else()
            message(WARNING "The board revision of this hardware is not known. Please add detection to this board in CMakeLists.txt. (proceeding to compile against a generic multicore CPU)")
            set(${IS_RPI} 0 PARENT_SCOPE)
        endif()
    endif()
endfunction()
