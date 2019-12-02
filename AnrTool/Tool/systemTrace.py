
from os.path import isfile,sep
from Tool import toolUtils
import re

UN_REGISTER_MAP = list()
def registerEventHandler(tag:str, action):
    if 'kEventTraceHeaderOpcode' == tag:
        tag = 'EventTraceParser.prototype.decodeHeader.bind(this)'
    elif 'kProcessStartOpcode' == tag:
        tag = 'ProcessParser.prototype.decodeStart.bind(this)'
    elif 'kProcessEndOpcode' == tag:
        tag = 'ProcessParser.prototype.decodeEnd.bind(this)'
    elif 'kProcessDCStartOpcode' == tag:
        tag = 'ProcessParser.prototype.decodeDCStart.bind(this)'
    elif 'kProcessDCEndOpcode' == tag:
        tag = 'ProcessParser.prototype.decodeDCEnd.bind(this)'
    elif 'kProcessDefunctOpcode' == tag:
        tag = 'ProcessParser.prototype.decodeDefunct.bind(this)'
    elif 'kThreadStartOpcode' == tag:
        tag = 'ThreadParser.prototype.decodeStart.bind(this)'
    elif 'kThreadEndOpcode' == tag:
        tag = 'ThreadParser.prototype.decodeEnd.bind(this)'
    elif 'kThreadDCStartOpcode' == tag:
        tag = 'ThreadParser.prototype.decodeDCStart.bind(this)'
    elif 'kThreadDCEndOpcode' == tag:
        tag = 'ThreadParser.prototype.decodeDCEnd.bind(this)'
    elif 'kThreadCSwitchOpcode' == tag:
        tag = 'ThreadParser.prototype.decodeCSwitch.bind(this)'
    elif 'opcode' == tag:
        tag = 'xxx'
    elif 'tracing_mark_write:android' == tag:
        tag = 'AndroidParser.prototype.traceMarkWriteAndroidEvent.bind(this)'
    elif '0:android' == tag:
        tag = 'AndroidParser.prototype.traceMarkWriteAndroidEvent.bind(this)'
    elif 'binder_locked' == tag:
        tag = 'BinderParser.prototype.binderLocked.bind(this)'
    elif 'binder_unlock' == tag:
        tag = 'BinderParser.prototype.binderUnlock.bind(this)'
    elif 'binder_lock' == tag:
        tag = 'BinderParser.prototype.binderLock.bind(this)'
    elif 'binder_transaction' == tag:
        tag = 'BinderParser.prototype.binderTransaction.bind(this)'
    elif 'binder_transaction_received' == tag:
        tag = 'BinderParser.prototype.binderTransactionReceived.bind(this)'
    elif 'binder_transaction_alloc_buf' == tag:
        tag = 'BinderParser.prototype.binderTransactionAllocBuf.bind(this)'
    elif 'memory_bus_usage' == tag:
        tag = 'BusParser.prototype.traceMarkWriteBusEvent.bind(this)'
    elif 'clock_set_rate' == tag:
        tag = ',ClockParser.prototype.traceMarkWriteClockEvent.bind(this)'
    elif 'clk_set_rate' == tag:
        tag = 'ClockParser.prototype.traceMarkWriteClkEvent.bind(this)'
    elif 'clock_enable' == tag:
        tag = 'ClockParser.prototype.traceMarkWriteClockOnOffEvent.bind(this)'
    elif 'clock_disable' == tag:
        tag = 'ClockParser.prototype.traceMarkWriteClockOnOffEvent.bind(this)'
    elif 'clk_enable' == tag:
        tag = 'ClockParser.prototype.traceMarkWriteClkOnEvent.bind(this)'
    elif 'clk_disable' == tag:
        tag = 'ClockParser.prototype.traceMarkWriteClkOffEvent.bind(this)'
    elif 'cpufreq_interactive_up' == tag:
        tag = 'CpufreqParser.prototype.cpufreqUpDownEvent.bind(this)'
    elif 'cpufreq_interactive_down' == tag:
        tag = 'CpufreqParser.prototype.cpufreqUpDownEvent.bind(this)'
    elif 'cpufreq_interactive_already' == tag:
        tag = 'CpufreqParser.prototype.cpufreqTargetEvent.bind(this)'
    elif 'cpufreq_interactive_notyet' == tag:
        tag = 'CpufreqParser.prototype.cpufreqTargetEvent.bind(this)'
    elif 'cpufreq_interactive_setspeed' == tag:
        tag = 'CpufreqParser.prototype.cpufreqTargetEvent.bind(this)'
    elif 'cpufreq_interactive_target' == tag:
        tag = 'CpufreqParser.prototype.cpufreqTargetEvent.bind(this)'
    elif 'cpufreq_interactive_boost' == tag:
        tag = 'CpufreqParser.prototype.cpufreqBoostUnboostEvent.bind(this)'
    elif 'cpufreq_interactive_unboost' == tag:
        tag = 'CpufreqParser.prototype.cpufreqBoostUnboostEvent.bind(this)'
    elif 'f2fs_write_begin' == tag:
        tag = 'DiskParser.prototype.f2fsWriteBeginEvent.bind(this)'
    elif 'f2fs_write_end' == tag:
        tag = 'DiskParser.prototype.f2fsWriteEndEvent.bind(this)'
    elif 'f2fs_sync_file_enter' == tag:
        tag = 'DiskParser.prototype.f2fsSyncFileEnterEvent.bind(this)'
    elif 'f2fs_sync_file_exit' == tag:
        tag = 'DiskParser.prototype.f2fsSyncFileExitEvent.bind(this)'
    elif 'ext4_sync_file_enter' == tag:
        tag = 'DiskParser.prototype.ext4SyncFileEnterEvent.bind(this)'
    elif 'ext4_sync_file_exit' == tag:
        tag = 'DiskParser.prototype.ext4SyncFileExitEvent.bind(this)'
    elif 'ext4_da_write_begin' == tag:
        tag = 'DiskParser.prototype.ext4WriteBeginEvent.bind(this)'
    elif 'ext4_da_write_end' == tag:
        tag = 'DiskParser.prototype.ext4WriteEndEvent.bind(this)'
    elif 'block_rq_issue' == tag:
        tag = 'DiskParser.prototype.blockRqIssueEvent.bind(this)'
    elif 'block_rq_complete' == tag:
        tag = 'DiskParser.prototype.blockRqCompleteEvent.bind(this)'
    elif 'drm_vblank_event' == tag:
        tag = 'DrmParser.prototype.vblankEvent.bind(this)'
    elif 'exynos_busfreq_target_int' == tag:
        tag = 'ExynosParser.prototype.busfreqTargetIntEvent.bind(this)'
    elif 'exynos_busfreq_target_mif' == tag:
        tag = 'ExynosParser.prototype.busfreqTargetMifEvent.bind(this)'
    elif 'exynos_page_flip_state' == tag:
        tag = 'ExynosParser.prototype.pageFlipStateEvent.bind(this)'
    elif 'fence_init' == tag:
        tag = 'FenceParser.prototype.initEvent.bind(this)'
    elif 'fence_destroy' == tag:
        tag = 'FenceParser.prototype.fenceDestroyEvent.bind(this)'
    elif 'fence_enable_signal' == tag:
        tag = 'FenceParser.prototype.fenceEnableSignalEvent.bind(this)'
    elif 'fence_signaled' == tag:
        tag = 'FenceParser.prototype.fenceSignaledEvent.bind(this)'
    elif 'tracing_mark_write:log' == tag:
        tag = 'GestureParser.prototype.logEvent.bind(this)'
    elif 'tracing_mark_write:SyncInterpret' == tag:
        tag = 'GestureParser.prototype.syncEvent.bind(this)'
    elif 'tracing_mark_write:HandleTimer' == tag:
        tag = 'GestureParser.prototype.timerEvent.bind(this)'
    elif 'i2c_write:HandleTimer' == tag:
        tag = 'I2cParser.prototype.i2cWriteEvent.bind(this)'
    elif 'i2c_read' == tag:
        tag = 'I2cParser.prototype.i2cReadEvent.bind(this)'
    elif 'i2c_write' == tag:
        tag = 'xx'
    elif 'i2c_reply' == tag:
        tag = 'I2cParser.prototype.i2cReplyEvent.bind(this)'
    elif 'i2c_result' == tag:
        tag = 'I2cParser.prototype.i2cResultEvent.bind(this)'
    elif 'i915_gem_object_create' == tag:
        tag = 'I915Parser.prototype.gemObjectCreateEvent.bind(this)'
    elif 'i915_gem_object_bind' == tag:
        tag = 'I915Parser.prototype.gemObjectBindEvent.bind(this)'
    elif 'i915_gem_object_unbind' == tag:
        tag = 'I915Parser.prototype.gemObjectBindEvent.bind(this)'
    elif 'i915_gem_object_change_domain' == tag:
        tag = 'I915Parser.prototype.gemObjectChangeDomainEvent.bind(this)'
    elif 'i915_gem_object_pread' == tag:
        tag = 'I915Parser.prototype.gemObjectPreadWriteEvent.bind(this)'
    elif 'i915_gem_object_pwrite' == tag:
        tag = 'I915Parser.prototype.gemObjectPreadWriteEvent.bind(this)'
    elif 'i915_gem_object_fault' == tag:
        tag = 'I915Parser.prototype.gemObjectFaultEvent.bind(this)'
    elif 'i915_gem_object_clflush' == tag:
        tag = 'I915Parser.prototype.gemObjectDestroyEvent.bind(this)'
    elif 'i915_gem_object_destroy' == tag:
        tag = 'I915Parser.prototype.gemObjectDestroyEvent.bind(this)'
    elif 'i915_gem_ring_dispatch' == tag:
        tag = 'I915Parser.prototype.gemRingDispatchEvent.bind(this)'
    elif 'i915_gem_ring_flush' == tag:
        tag = 'I915Parser.prototype.gemRingFlushEvent.bind(this)'
    elif 'i915_gem_request' == tag:
        tag = 'I915Parser.prototype.gemRequestEvent.bind(this)'
    elif 'i915_gem_request_add' == tag:
        tag = 'I915Parser.prototype.gemRequestEvent.bind(this)'
    elif 'i915_gem_request_complete' == tag:
        tag = 'I915Parser.prototype.gemRequestEvent.bind(this)'
    elif 'i915_gem_request_retire' == tag:
        tag = 'I915Parser.prototype.gemRequestEvent.bind(this)'
    elif 'i915_gem_request_wait_begin' == tag:
        tag = 'I915Parser.prototype.gemRequestEvent.bind(this)'
    elif 'i915_gem_request_wait_end' == tag:
        tag = 'I915Parser.prototype.gemRequestEvent.bind(this)'
    elif 'i915_gem_ring_wait_begin' == tag:
        tag = 'I915Parser.prototype.gemRingWaitEvent.bind(this)'
    elif 'i915_gem_ring_wait_end' == tag:
        tag = 'I915Parser.prototype.gemRingWaitEvent.bind(this)'
    elif 'i915_reg_rw' == tag:
        tag = 'I915Parser.prototype.regRWEvent.bind(this)'
    elif 'i915_flip_request' == tag:
        tag = 'I915Parser.prototype.flipEvent.bind(this)'
    elif 'i915_flip_complete' == tag:
        tag = 'I915Parser.prototype.flipEvent.bind(this)'
    elif 'intel_gpu_freq_change' == tag:
        tag = 'I915Parser.prototype.gpuFrequency.bind(this)'
    elif 'irq_handler_entry' == tag:
        tag = 'IrqParser.prototype.irqHandlerEntryEvent.bind(this)'
    elif 'irq_handler_exit' == tag:
        tag = 'IrqParser.prototype.irqHandlerExitEvent.bind(this)'
    elif 'softirq_raise' == tag:
        tag = 'IrqParser.prototype.softirqRaiseEvent.bind(this)'
    elif 'softirq_entry' == tag:
        tag = 'IrqParser.prototype.softirqEntryEvent.bind(this)'
    elif 'softirq_exit' == tag:
        tag = 'IrqParser.prototype.softirqExitEvent.bind(this)'
    elif 'ipi_entry' == tag:
        tag = 'IrqParser.prototype.ipiEntryEvent.bind(this)'
    elif 'ipi_exit' == tag:
        tag = 'IrqParser.prototype.ipiExitEvent.bind(this)'
    elif 'preempt_disable' == tag:
        tag = 'IrqParser.prototype.preemptStartEvent.bind(this)'
    elif 'preempt_enable' == tag:
        tag = 'IrqParser.prototype.preemptEndEvent.bind(this)'
    elif 'irq_disable' == tag:
        tag = 'IrqParser.prototype.irqoffStartEvent.bind(this)'
    elif 'irq_enable' == tag:
        tag = 'IrqParser.prototype.irqoffEndEvent.bind(this)'
    elif 'graph_ent' == tag:
        tag = 'KernelFuncParser.prototype.traceKernelFuncEnterEvent.bind(this)'
    elif 'graph_ret' == tag:
        tag = 'KernelFuncParser.prototype.traceKernelFuncReturnEvent.bind(this)'
    elif 'mali_dvfs_event' == tag:
        tag = 'MaliParser.prototype.dvfsEventEvent.bind(this)'
    elif 'mali_dvfs_set_clock' == tag:
        tag = 'MaliParser.prototype.dvfsSetClockEvent.bind(this)'
    elif 'mali_dvfs_set_voltage' == tag:
        tag = 'MaliParser.prototype.dvfsSetVoltageEvent.bind(this)'
    elif 'tracing_mark_write:mali_driver' == tag:
        tag = 'MaliParser.prototype.maliDDKEvent.bind(this)'
    elif 'mali_job_systrace_event_start' == tag:
        tag = 'MaliParser.prototype.maliJobEvent.bind(this)'
    elif 'mali_job_systrace_event_stop' == tag:
        tag = ',MaliParser.prototype.maliJobEvent.bind(this)'
    elif 'mm_vmscan_kswapd_wake' == tag:
        tag = 'MemReclaimParser.prototype.kswapdWake.bind(this)'
    elif 'mm_vmscan_kswapd_sleep' == tag:
        tag = 'MemReclaimParser.prototype.kswapdSleep.bind(this)'
    elif 'mm_vmscan_direct_reclaim_begin' == tag:
        tag = 'MemReclaimParser.prototype.reclaimBegin.bind(this)'
    elif 'mm_vmscan_direct_reclaim_end' == tag:
        tag = 'MemReclaimParser.prototype.reclaimEnd.bind(this)'
    elif 'lowmemory_kill' == tag:
        tag = 'MemReclaimParser.prototype.lowmemoryKill.bind(this)'
    elif 'power_start' == tag:
        tag = 'PowerParser.prototype.powerStartEvent.bind(this)'
    elif 'power_frequency' == tag:
        tag = 'PowerParser.prototype.powerFrequencyEvent.bind(this)'
    elif 'cpu_frequency' == tag:
        tag = 'PowerParser.prototype.cpuFrequencyEvent.bind(this)'
    elif 'cpu_frequency_limits' == tag:
        tag = 'PowerParser.prototype.cpuFrequencyLimitsEvent.bind(this)'
    elif 'cpu_idle' == tag:
        tag = 'PowerParser.prototype.cpuIdleEvent.bind(this)'
    elif 'regulator_enable' == tag:
        tag = 'RegulatorParser.prototype.regulatorEnableEvent.bind(this)'
    elif 'regulator_enable_delay' == tag:
        tag = 'RegulatorParser.prototype.regulatorEnableDelayEvent.bind(this)'
    elif 'regulator_enable_complete' == tag:
        tag = 'RegulatorParser.prototype.regulatorEnableCompleteEvent.bind(this)'
    elif 'regulator_disable' == tag:
        tag = 'RegulatorParser.prototype.regulatorDisableEvent.bind(this)'
    elif 'regulator_disable_complete' == tag:
        tag = 'RegulatorParser.prototype.regulatorDisableCompleteEvent.bind(this)'
    elif 'regulator_set_voltage' == tag:
        tag = 'RegulatorParser.prototype.regulatorSetVoltageEvent.bind(this)'
    elif 'regulator_set_voltage_complete' == tag:
        tag = 'RegulatorParser.prototype.regulatorSetVoltageCompleteEvent.bind(this)'
    elif 'sched_switch' == tag:
        tag = 'SchedParser.prototype.schedSwitchEvent.bind(this)'
    elif 'sched_waking' == tag:
        tag = 'SchedParser.prototype.schedSwitchEvent.bind(this)'
    elif 'sched_wakeup' == tag:
        tag = 'SchedParser.prototype.schedSwitchEvent.bind(this)'
    elif 'sched_blocked_reason' == tag:
        tag = 'SchedParser.prototype.schedBlockedEvent.bind(this)'
    elif 'sched_cpu_hotplug' == tag:
        tag = 'SchedParser.prototype.schedCpuHotplugEvent.bind(this)'
    elif 'sync_timeline' == tag:
        tag = 'SyncParser.prototype.timelineEvent.bind(this)'
    elif 'sync_wait' == tag:
        tag = 'SyncParser.prototype.syncWaitEvent.bind(this)'
    elif 'sync_pt' == tag:
        tag = 'SyncParser.prototype.syncPtEvent.bind(this)'
    elif 'workqueue_execute_start' == tag:
        tag = 'WorkqueueParser.prototype.executeStartEvent.bind(this)'
    elif 'workqueue_execute_end' == tag:
        tag = 'WorkqueueParser.prototype.executeEndEvent.bind(this)'
    elif 'workqueue_queue_work' == tag:
        tag = 'WorkqueueParser.prototype.executeQueueWork.bind(this)'
    elif 'workqueue_activate_work' == tag:
        tag = 'WorkqueueParser.prototype.executeActivateWork.bind(this)'
    elif 'tracing_mark_write' == tag:
        tag = 'FTraceImporter.prototype.traceMarkingWriteEvent_.bind(this)'
    elif '0' == tag:
        tag = 'FTraceImporter.prototype.traceMarkingWriteEvent_.bind(this)'
    elif 'cgroup_attach_task' == tag:
        tag = 'xx'
    elif 'cgroup_release' == tag:
        tag = 'xx'
    elif 'cgroup_rmdir' == tag:
        tag = 'xx'
    elif 'dma_fence_destroy' == tag:
        tag = 'xx'
    elif 'dma_fence_enable_signal' == tag:
        tag = 'xx'
    elif 'dma_fence_init' == tag:
        tag = 'xx'
    elif 'dma_fence_signaled' == tag:
        tag = 'xx'
    elif 'hrtimer_cancel' == tag:
        tag = 'xx'
    elif 'hrtimer_expire_entry' == tag:
        tag = 'xx'
    elif 'hrtimer_expire_exit' == tag:
        tag = 'xx'
    elif 'hrtimer_init' == tag:
        tag = 'xx'
    elif 'hrtimer_start' == tag:
        tag = 'xx'
    elif 'mm_filemap_add_to_page_cache' == tag:
        tag = 'xx'
    elif 'mm_filemap_delete_from_page_cache' == tag:
        tag = 'xx'
    elif 'oom_score_adj_update' == tag:
        tag = 'xx'
    elif 'rpmh_send_msg' == tag:
        tag = 'xx'
    elif 'sched_isolate' == tag:
        tag = 'xx'
    elif 'sched_migrate_task' == tag:
        tag = 'xx'
    elif 'sched_pi_setprio' == tag:
        tag = 'xx'
    elif 'sched_process_exit' == tag:
        tag = 'xx'
    elif 'sched_wakeup_new' == tag:
        tag = 'xx'
    elif 'sde_evtlog' == tag:
        tag = 'xx'
    elif 'sde_perf_calc_crtc' == tag:
        tag = 'xx'
    elif 'sde_perf_crtc_update' == tag:
        tag = 'xx'
    elif 'sde_perf_set_danger_luts' == tag:
        tag = 'xx'
    elif 'sde_perf_set_qos_luts' == tag:
        tag = 'xx'
    elif 'task_newtask' == tag:
        tag = 'xx'
    elif 'task_rename' == tag:
        tag = 'xx'
    elif 'timer_expire_entry' == tag:
        tag = 'xx'
    elif 'timer_expire_exit' == tag:
        tag = 'xx'
    elif 'eventName' == tag:
        tag = 'xx'
    elif 'eventName' == tag:
        tag = 'xx'
    elif 'tracing_mark_write:trace_event_clock_sync' == tag:
        tag = 'xxx'
    elif '0:trace_event_clock_sync' == tag:
        tag = 'xxx'
    elif 'hwcEventName' == tag:
        tag = 'xx'
    else:
        print("tag={}  ###  action={}".format(tag, action))
        if not tag in UN_REGISTER_MAP:
            UN_REGISTER_MAP.append(tag)

class TraceFunction:
    '''
    cpu_pred_hist: idx:0 resi:13 sample:4 tmr:0
    '''
    PATTERN_LINE = '^[\ ]*([^:]+):[\ ]*(.*)'
    def __init__(self, function:str):
        self.function = function
        match = re.match(TraceFunction.PATTERN_LINE, function)

        if match:
            registerEventHandler(match.group(1).strip(), match.group(2).strip())

class TraceLine:
    PATTERN_LINE = '^[\ ]*([^-]+)-([\d]+)[\ ]+\(([\d|-|\ ]+)\)[\ ]+\[([\d]+)\][\ ]+([\w|\d|\.])([\w|\d|\.])([\w|\d|\.])([\w|\d|\.])[\ ]+([\w|\.]+):(.*)'
    '''
    <!-- BEGIN TRACE -->
      <script class="trace-data" type="application/text">
    # tracer: nop
    #
    # entries-in-buffer/entries-written: 201593/201593   #P:8
    #
    #                                      _-----=> irqs-off
    #                                     / _----=> need-resched
    #                                    | / _---=> hardirq/softirq
    #                                    || / _--=> preempt-depth
    #                                    ||| /     delay
    #           TASK-PID    TGID   CPU#  ||||    TIMESTAMP  FUNCTION
    #              | |        |      |   ||||       |         |
              <idle>-0     (-----) [002] dn.1  1507.655129: cpu_pred_hist: idx:0 resi:13 sample:4 tmr:0
               <...>-976   (  922) [003] d..4  1507.655130: sched_wakeup: comm=ndroid.systemui pid=2217 prio=110 target_cpu=002
         OomAdjuster-1466  ( 1070) [006] ....  1509.655935: cgroup_attach_task: dst_root=2 dst_id=2 dst_level=1 dst_path=/background pid=5747 comm=Thread-20
      </script>
    <!-- END TRACE -->
    '''
    IRQ_OFF_MAP = list()
    NEED_RESCHED = list()
    IRQ = list()
    PREEMPT_DEPTH = list()
    def __init__(self, task:str, pid:int, tgid:int, cpuId:int, irqsOff:str, needResched:str, irq:str, preemptDepth:str, timestamp:float, function:TraceFunction):
        '''
        :param task: name or ... or idle 名称
        :param pid: 进程id
        :param tgid: 线程id
        :param cpuId: 使用的cpu号
        :param irqsOff: 终端请求了 ['d', '.']
        :param needResched: 需要resched ['.', 'n']
        :param irq: 中断['.', 'h', 's', 'H']
        :param preemptDepth: 优先等级['4', '1', '.', '2', '3', '5', '8', '9', 'a', '7', '6', 'b', 'c', 'd']
        :param timestamp: 时间戳
        :param function:
        '''
        self.task:str = task
        self.pid: int = pid
        self.tgid: int = tgid
        self.cpuId: int = cpuId
        self.irqsOff: chr = irqsOff
        if not irqsOff in TraceLine.IRQ_OFF_MAP:
            TraceLine.IRQ_OFF_MAP.append(irqsOff)
        self.needResched: chr = needResched
        if not needResched in TraceLine.NEED_RESCHED:
            TraceLine.NEED_RESCHED.append(needResched)
        self.irq: chr = irq
        if not irq in TraceLine.IRQ:
            TraceLine.IRQ.append(irq)
        self.preemptDepth: chr = preemptDepth
        if not preemptDepth in TraceLine.PREEMPT_DEPTH:
            TraceLine.PREEMPT_DEPTH.append(preemptDepth)
        self.timestamp: float = timestamp
        self.function: TraceFunction = function


class SystemTrace:
    def __init__(self, trace_html:str):
        self.traceHtml = trace_html
        self.lines:TraceLine = []
        #{'key_pid':{key_tgid:TraceLine}}
        self.pidTraceDict = dict()
        print(isfile(trace_html))
        if not isfile(trace_html) or not trace_html.endswith('.html'):
            self.isTraceFile = False
        else:
            self.isTraceFile = True
    def parseLine(self, line:str):
        match = re.match(TraceLine.PATTERN_LINE, line)
        if match:
            #name or ... or idle 名称
            task:str = match.group(1).strip()
            #pid 进程id
            pid:int = int(match.group(2).strip())
            #tgid 线程id
            tgid:int = int(match.group(3).strip())
            #cpuId 使用的cpu号
            cpuId:int = int(match.group(4).strip())
            #irqs-off 终端请求了 ['d', '.']
            irqsOff:str = str(match.group(5).strip())
            #need-resched 需要resched ['.', 'n']
            needResched:str = str(match.group(6).strip())
            #hardirq/softirq 中断['.', 'h', 's', 'H']
            irq:str = str(match.group(7).strip())
            #preempt-depth 优先等级['4', '1', '.', '2', '3', '5', '8', '9', 'a', '7', '6', 'b', 'c', 'd']
            preemptDepth:str = str(match.group(8).strip())
            #TIMESTAMP 时间戳
            timestamp:float = float(match.group(9).strip())
            #FUNCTION 方法
            function:TraceFunction = TraceFunction(match.group(10).strip())
            return TraceLine(task, pid, tgid, cpuId, irqsOff, needResched, irq, preemptDepth, timestamp, function)
        else:
            return None

    def __addTraceLine__(self, line:TraceLine):
        self.lines.append(line)
        pidKey = 'key_{}'.format(line.pid)
        pidTrace = None
        if pidKey in self.pidTraceDict.keys():
            pidTrace = self.pidTraceDict[pidKey]
        else:
            pidTrace = dict()
            self.pidTraceDict[pidKey] = pidTrace
        tgidKey = 'key_{}'.format(line.tgid)
        tgidList = None
        if tgidKey in self.pidTraceDict.keys():
            tgidList =pidTrace[tgidKey]
        else:
            tgidList = list()
            self.pidTraceDict[tgidKey] = tgidList
        tgidList.append(line)



    def parseTrace(self):
        if self.isTraceFile:
            beginTrace = False
            with open(self.traceHtml, encoding=toolUtils.checkFileCode(self.traceHtml)) as mFile:
                linenum = 0
                while True:
                    linenum = linenum+1
                    line = mFile.readline()
                    if not line:
                        break
                    elif '<!-- BEGIN TRACE -->' in line:
                        beginTrace = True
                    elif '<!-- END TRACE -->' in line:
                        beginTrace = False
                    elif beginTrace:
                        temp:TraceLine = self.parseLine(line)
                        if temp:
                            self.lines.append(temp)
            print('IRQ_OFF_MAP = {}'.format(TraceLine.IRQ_OFF_MAP))
            print('NEED_RESCHED = {}'.format(TraceLine.NEED_RESCHED))
            print('IRQ = {}'.format(TraceLine.IRQ))
            print('PREEMPT_DEPTH = {}'.format(TraceLine.PREEMPT_DEPTH))
            UN_REGISTER_MAP.sort()
            print('UN_REGISTER_MAP = {}'.format(UN_REGISTER_MAP))


if __name__ == '__main__':
    '''    
    #                                      _-----=> irqs-off
    #                                     / _----=> need-resched
    #                                    | / _---=> hardirq/softirq
    #                                    || / _--=> preempt-depth
    #                                    ||| /     delay
    #           TASK-PID    TGID   CPU#  ||||    TIMESTAMP  FUNCTION
    #              | |        |      |   ||||       |         |
              <idle>-0     (-----) [002] dn.1  1507.655129: cpu_pred_hist: idx:0 resi:13 sample:4 tmr:0
    '''
    line = '         OomAdjuster-1466  ( 1070) [006] ....  1509.655738: cgroup_attach_task: dst_root=6 dst_id=3 dst_level=1 dst_path=/background pid=5746 comm=Thread-19'
    pattern = '^[\ ]*([^-]+)-([\d]+)[\ ]+\(([\d|-|\ ]+)\)[\ ]+\[([\d]+)\][\ ]+([\w|\d|\.])([\w|\d|\.])([\w|\d|\.])([\w|\d|\.])[\ ]+([\w|\.]+):(.*)'
    match = re.match(pattern, line)
    if match:
        print(match.groups())
    trace_html = sep.join(['..','res', 'trace.html'])
    trace = SystemTrace(trace_html)
    trace.parseTrace()