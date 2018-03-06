# Copyright (C) 2013,2015 ARM Limited. All rights reserved.

from osapi import *
from rtxInfoV5 import RtxInfoV5
from rtxIterator import *

RTX_DATA_MODEL = RtxInfoV5()

def getKernelState(dbg):
    return RTX_DATA_MODEL.getKernelState(dbg)

def getControlBlockIdentifiers():
    return RTX_DATA_MODEL.getControlBlockIdentifiers()
    
def getControlBlockId(cbName):
    return getControlBlockIdentifiers()[cbName]

def getControlBlockName(cbId):
    return next((name for (name, id) in getControlBlockIdentifiers().items() if id == cbId), None)

def getControlBlockIdentifierFromPointer(cbPtr):
    return getControlBlockName(getPtrMemBers(cbPtr)["id"].readAsNumber())

def isThreadControlBlock(cbPtr):
    return getControlBlockIdentifiers()['Thread'] == getPtrMemBers(cbPtr)["id"].readAsNumber()

def makeNumberCell(members, name):
    return createNumberCell(members[name].readAsNumber() if (name in members) else None)

def getCType(cbName):
    return RTX_DATA_MODEL.getCType(cbName)

def getCurrentTask(dbg):
    return RTX_DATA_MODEL.getCurrentTask(dbg)

def getTaskIdType():
    return RTX_DATA_MODEL.getTaskIdType()

def getActiveTasks(dbg):
    return RTX_DATA_MODEL.getActiveTasks(dbg)

def getTaskId(tcbPtr, members):
    return RTX_DATA_MODEL.getTaskId(tcbPtr, members)

def getDisplayableTaskId(tcbPtr, members):
    return RTX_DATA_MODEL.getDisplayableTaskId(tcbPtr, members)

def makeNumberCell(members, name):
    return createNumberCell(members[name].readAsNumber() if (name in members) else None)
    
def makeAddressCell(members, name):
    return createAddressCell(member[name].readAsAddress())

def makeAddressOfCell(members, name):
    return createAddressCell(member[name].getLocationAddress())

def makeNameCell(members, name):
    return createTextCell(getSimpleName(members, name))

def makeTaskIdCell(tcbPtr, members):
    return createTextCell(RTX_DATA_MODEL.getDisplayableTaskId(tcbPtr, members))

def makeTaskCell(members, name):
    return makeTaskIdCell(members[name], members[name].dereferencePointer().getStructureMembers())

def makeStateCell(members):
    return createTextCell(getTaskState(members["state"].readAsNumber(), members))

def makeTaskWaitersCell(members, name):
    tcbPtr = members[name]
    result = []

    while nonNullPtr(tcbPtr):
        members = getPtrMemBers(tcbPtr)
        result.append(str(RTX_DATA_MODEL.getDisplayableTaskId(tcbPtr, members)))
        tcbPtr = members["thread_next"]

    return createTextCell(', '.join(result))
    
def getSimpleName(members, name):
    member = members[name]
    location = member.resolveAddressAsString()
    index = location.find("+")
    if(index != -1):
        location = str(location)[:index]

    return location

def getTaskState(stateId, members=None):
    return RTX_DATA_MODEL.getTaskState(stateId, members)
    
def dereferenceThreadPointer(tcbPtr):
    return tcbPtr.dereferencePointer(getCType("Thread"))

def isStackOverflowCheckEnabled(dbg):
    if RTX_DATA_MODEL.isStackOverflowCheckEnabled(dbg):
        return "system.stack_overflow_check.yes"
    else:
        return "system.stack_overflow_check.no"

def isStackUsageWatermarkEnabled(dbg):
    if RTX_DATA_MODEL.isStackUsageWatermarkEnabled(dbg):
        return "system.stack_usage_watermark.yes"
    else:
        return "system.stack_usage_watermark.no"

def getStackSize(members, dbg):
    return RTX_DATA_MODEL.getStackSize(members, dbg)   
    
def nextPtr(ptr, nextMemberName):
    return getPtrMemBers(ptr)[nextMemberName]

def getPtrMemBers(ptr, type=None):
    if type:
        return ptr.dereferencePointer(type).getStructureMembers()
    else:
        return ptr.dereferencePointer().getStructureMembers()
    
def isNullPtr(ptr):
    return ptr.readAsNumber() == 0

def nonNullPtr(ptr):
    return ptr.readAsNumber() != 0
    
# turn to int/long to hex without the irritating "L" added to the end for longs
def toHex(x):
    return "0x%X" % x

# Base class for task control block structures
class RtxTable(Table):

    def __init__(self, id, fields):
        Table.__init__(self, id, fields)

    def getRecords(self, dbg):
        return list(map(lambda cbPtr: self.createRecordFromControlBlock(cbPtr, dbg), self.getControlBlocks(dbg)))

    def getControlBlocks(self, dbg):
        return getActiveTasks(dbg)

    def createRecordFromControlBlock(self, cbPtr, dbg):
        raise NotImplementedError
        
        
class RtxInterTaskCommTable(RtxTable):

    def __init__(self, id, fields, functions, tcbType):
        RtxTable.__init__(self, id, fields)
        self.functions = functions
        self.tcbType   = tcbType

    def getRecords(self, dbg):
        records = []
        for tcbPtr in self.getControlBlocks(dbg):
            if nonNullPtr(tcbPtr):

                threadPrev = dereferenceThreadPointer(tcbPtr).getStructureMembers()["thread_prev"]

                if nonNullPtr(threadPrev):
                    cells = self.createRecordFromControlBlock(threadPrev, dbg)

                    if cells:
                        records.append(self.createRecord(cells))

        return records

    def createRecordFromControlBlock(self, threadPrev, dbg):
        members = threadPrev.dereferencePointer(getCType(self.tcbType)).getStructureMembers()

        if (members["id"].readAsNumber() == getControlBlockId(self.tcbType)):
            return [function(members, threadPrev) for function in self.functions]

        return []
