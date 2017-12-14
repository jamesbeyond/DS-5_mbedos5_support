# Copyright (C) 2013,2015 ARM Limited. All rights reserved.

from osapi import *
from tasks import Tasks
from stacks import Stacks
from mailboxes import Mailboxes
from mutexes import Mutexes
from semaphores import Semaphores
from system import System
from contexts import ContextsProvider
from com.arm.debug.extension import DebugSessionException

# this script effectively implements com.arm.debug.extension.os.IOSProvider

def getOSContextProvider():
    return ContextsProvider()

def getDataModel():
    return Model("mbedos5", [Tasks(), Stacks(), Mailboxes(), Mutexes(), Semaphores(), System()])

def isOSInitialised(debugger):
    try:
        return debugger.evaluateExpression("os_running").readAsNumber() == 1
    except DebugSessionException:
        return False;

def areOSSymbolsLoaded(debugger):
    return debugger.symbolExists("os_active_TCB")
