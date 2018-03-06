# Copyright (C) 2013,2015 ARM Limited. All rights reserved.

from osapi import *
from contexts import ContextsProvider
from com.arm.debug.extension import DebugSessionException

from tasks import Tasks
from timers import Timers
from stacks import Stacks
from mailboxes import Mailboxes
from messagequeues import MessageQueues
from memorypools import MemoryPools
from mutexes import Mutexes
from semaphores import Semaphores
from system import System

# this script effectively implements com.arm.debug.extension.os.IOSProvider

def getOSContextProvider():
    return ContextsProvider()

def getDataModel():
    return Model("mbedos5", [Tasks(), Timers(), Stacks(), MemoryPools(), Mailboxes(), MessageQueues(), Mutexes(), Semaphores(), System()])

def isOSInitialised(debugger):
    try:
        return debugger.evaluateExpression("osRtxInfo.kernel.state").readAsNumber() >= 1
    except DebugSessionException:
        return False;

def areOSSymbolsLoaded(debugger):
    return debugger.symbolExists("osRtxInfo")
