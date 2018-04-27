# Copyright (C) 2018 Arm Limited (or its affiliates). All rights reserved.

from itertools import chain
from osapi import TEXT
from rtxIterator import *

class Rtx5:

    KERNEL_STATE_READY       = 1
    KERNEL_STATE_RUNNING     = 2

    OS_FLAGS_WAIT_ANY        = 0x00000000L    #Wait for any flag (default).
    OS_FLAGS_WAIT_ALL        = 0x00000001L    #Wait for all flags.

    ControlBlockIdentifier = {
        'Invalid'         : 0,
        'Thread'          : 1,
        'Timer'           : 2,
        'EventFlags'      : 3,
        'Mutex'           : 4,
        'Semaphore'       : 5,
        'MemoryPool'      : 6,
        'Message'         : 7,
        'MessageQueue'    : 8
    }

    kernelState = {
        0                 : 'osKernelInactive',         # Inactive.
        1                 : 'osKernelReady',            # Ready.
        2                 : 'osKernelRunning',          # Running.
        3                 : 'osKernelLocked',           # Locked.
        4                 : 'osKernelSuspended',        # Suspended.
        -1                : 'osKernelError',            # Error.
    }

    THREAD_BLOCKED_STATE_ID  = 3

    THREAD_STATES = {
        0                                : "INACTIVE",
        1                                : "READY",
        2                                : "RUNNING",
        THREAD_BLOCKED_STATE_ID          : "BLOCKED",
        4                                : "TERMINATED",
        (THREAD_BLOCKED_STATE_ID | 0x10) : "WAIT_DELAY",
        (THREAD_BLOCKED_STATE_ID | 0x20) : "WAIT_JOIN",
        (THREAD_BLOCKED_STATE_ID | 0x30) : "WAIT_THREAD_FLAGS",
        (THREAD_BLOCKED_STATE_ID | 0x40) : "WAIT_EVENT_FLAGS",
        (THREAD_BLOCKED_STATE_ID | 0x50) : "WAIT_MUTEX",
        (THREAD_BLOCKED_STATE_ID | 0x60) : "WAIT_SEMAPHORE",
        (THREAD_BLOCKED_STATE_ID | 0x70) : "WAIT_MEMORY_POOL",
        (THREAD_BLOCKED_STATE_ID | 0x80) : "WAIT_MESSAGE_GET",
        (THREAD_BLOCKED_STATE_ID | 0x90) : "WAIT_MESSAGE_PUT"
    }
    
    @classmethod
    def isKernelInitialised(cls, dbg):
        kernel_state = dbg.evaluateExpression("osRtxInfo.kernel.state").readAsNumber()
        return (kernel_state==cls.KERNEL_STATE_READY) or (kernel_state==cls.KERNEL_STATE_RUNNING)
    
    @classmethod
    def getKernelState(cls, dbg):
        kernel_state = dbg.evaluateExpression("osRtxInfo.kernel.state").readAsNumber()
        return cls.kernelState[kernel_state]
    
    @classmethod
    def getCType(cls, cbName):
        return "osRtx" + cbName + "_t*"
        
    @classmethod
    def getActiveTasks(cls, dbg):
        return chain(toIterator(dbg, "osRtxInfo.thread.run.curr", ""),
                 toIterator(dbg, "osRtxInfo.thread.ready.thread_list", "thread_next"),
                 toIterator(dbg, "osRtxInfo.thread.delay_list", "delay_next"),
                 toIterator(dbg, "osRtxInfo.thread.wait_list",  "delay_next"))

    @classmethod
    def getTaskIdType(cls):
        return TEXT #address
    
    @classmethod
    def getTaskId(cls, tcbPtr, members):
        return tcbPtr.readAsNumber()

    @classmethod
    def getDisplayableTaskId(cls, tcbPtr, members):
        return "0x" + str(cls.getTaskId(tcbPtr, members))
    
    @classmethod
    def getCurrentTask(cls, dbg):
        return dbg.evaluateExpression("osRtxInfo.thread.run.curr")

    @classmethod
    def getTaskState(cls, stateId, members=None):
        if((stateId & 0x0F) != cls.THREAD_BLOCKED_STATE_ID):
            stateId = stateId & 0x0F

        name = cls.THREAD_STATES[stateId]

        if (members and ((name == "WAIT_THREAD_FLAGS") or (name == "WAIT_EVENT_FLAGS"))):
            flagsOption = members["flags_options"].readAsNumber()
            name += "_ALL" if ((flagsOption & cls.OS_FLAGS_WAIT_ALL) != 0) else "_ANY"

        return name if name else str(stateId)
        
    @classmethod
    def getControlBlockIdentifiers(cls):
        return cls.ControlBlockIdentifier

    @classmethod
    def getStackInfo(cls, dbg):
        return dbg.evaluateExpression("osRtxConfig.flags").readAsNumber()

    @classmethod
    def isStackUsageWatermarkEnabled(cls, dbg):
        return (cls.getStackInfo(dbg) & 0x4) != 0

    @classmethod
    def isStackOverflowCheckEnabled(cls, dbg):
        return (cls.getStackInfo(dbg) & 0x2) != 0

    @classmethod
    def getStackSize(cls, members, dbg):
        return members["stack_size"].readAsNumber()
