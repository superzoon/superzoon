
@echo Usage: main.py [options] [category1 [category2 ...]]

@echo Example: main.py -b 32768 -t 15 gfx input view sched freq

@echo Options:
@echo   -h, --help            show this help message and exit
@echo   -o FILE               write trace output to FILE
@echo   -j, --json            write a JSON file
@echo   --link-assets         (deprecated)
@echo   --asset-dir=ASSET_DIR
@echo                         (deprecated)
@echo   -e DEVICE_SERIAL_NUMBER, --serial=DEVICE_SERIAL_NUMBER
@echo                         adb device serial number
@echo   --target=TARGET       choose tracing target (android or linux)
@echo   --timeout=TIMEOUT     timeout for start and stop tracing (seconds)
@echo   --collection-timeout=COLLECTION_TIMEOUT
@echo                         timeout for data collection (seconds)
@echo   -t N, --time=N        trace for N seconds
@echo   -b N, --buf-size=N    use a trace buffer size  of N KB
@echo   -l, --list-categories
@echo                         list the available categories and exit
@echo 
@echo   Atrace options:
@echo     --atrace-categories=ATRACE_CATEGORIES
@echo                         Select atrace categories with a comma-delimited list,
@echo                         e.g. --atrace-categories=cat1,cat2,cat3
@echo     -k KFUNCS, --ktrace=KFUNCS
@echo                         specify a comma-separated list of kernel functions to
@echo                         trace
@echo     --no-compress       Tell the device not to send the trace data in
@echo                         compressed form.
@echo     -a APP_NAME, --app=APP_NAME
@echo                         enable application-level tracing for comma-separated
@echo                         list of app cmdlines
@echo     --from-file=FROM_FILE
@echo                         read the trace from a file (compressed) rather than
@echo                         running a live trace
@echo 
@echo   Atrace process dump options:
@echo     --process-dump      Capture periodic per-process memory dumps.
@echo     --process-dump-interval=PROCESS_DUMP_INTERVAL_MS
@echo                         Interval between memory dumps in milliseconds.
@echo     --process-dump-full=PROCESS_DUMP_FULL_CONFIG
@echo                         Capture full memory dumps for some processes. Value:
@echo                         all, apps or comma-separated process names.
@echo     --process-dump-mmaps
@echo                         Capture VM regions and memory-mapped files. It
@echo                         increases dump size dramatically, hence only has
@echo                         effect if --process-dump-full is a whitelist.
@echo 
@echo   Ftrace options:
@echo     --ftrace-categories=FTRACE_CATEGORIES
@echo                         Select ftrace categories with a comma-delimited list,
@echo                         e.g. --ftrace-categories=cat1,cat2,cat3
@echo 
@echo   WALT trace options:
@echo     --walt              Use the WALT tracing agent. WALT is a device for
@echo                         measuring latency of physical sensors on phones and
@echo                         computers. See https://github.com/google/walt
@echo                         
@echo        gfx - Graphics
@echo        input - Input
@echo         view - View System
@echo      webview - WebView
@echo           wm - Window Manager
@echo           am - Activity Manager
@echo           sm - Sync Manager
@echo        audio - Audio
@echo        video - Video
@echo       camera - Camera
@echo          hal - Hardware Modules
@echo          res - Resource Loading
@echo       dalvik - Dalvik VM
@echo           rs - RenderScript
@echo       bionic - Bionic C Library
@echo        power - Power Management
@echo           pm - Package Manager
@echo           ss - System Server
@echo     database - Database
@echo      network - Network
@echo          adb - ADB
@echo     vibrator - Vibrator
@echo         aidl - AIDL calls
@echo        nnapi - NNAPI
@echo          rro - Runtime Resource Overlay
@echo          pdx - PDX services
@echo        sched - CPU Scheduling
@echo          irq - IRQ Events
@echo          i2c - I2C Events
@echo         freq - CPU Frequency
@echo         idle - CPU Idle
@echo         disk - Disk I/O
@echo         sync - Synchronization
@echo        workq - Kernel Workqueues
@echo   memreclaim - Kernel Memory Reclaim
@echo   regulators - Voltage and Current Regulators
@echo   binder_driver - Binder Kernel driver
@echo   binder_lock - Binder global lock trace
@echo    pagecache - Page cache
@echo          gfx - Graphics (HAL)
@echo          ion - ION allocation (HAL)
@echo 
@echo NOTE: more categories may be available with adb root


@echo "list-categories gfx input view wm am sm hal power ss aidl sched idle freq binder_driver binder_lock"
SystraceTool\SystraceTool.exe -b 10240 -t 5 -a com.android.systemui gfx input view wm am sm -o d:\systrace_trace_viewer.html
pause