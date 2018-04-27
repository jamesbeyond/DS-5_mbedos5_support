# Copyright (C) 2013,2015 ARM Limited. All rights reserved.

from osapi import *
from rtxInfo import Rtx5
from rtxIterator import *


def getControlBlockId(cbName):
    return Rtx5.getControlBlockIdentifiers()[cbName]

def getControlBlockName(cbId):
    return next((name for (name, id) in Rtx5.getControlBlockIdentifiers().items() if id == cbId), None)

def getControlBlockIdentifierFromPointer(cbPtr):
    return getControlBlockName(getPtrMemBers(cbPtr)["id"].readAsNumber())

def isThreadControlBlock(cbPtr):
    return Rtx5.getControlBlockIdentifiers()['Thread'] == getPtrMemBers(cbPtr)["id"].readAsNumber()

def makeNumberCell(members, name):
    return createNumberCell(members[name].readAsNumber() if (name in members) else None)

def makeNumberCell(members, name):
    return createNumberCell(members[name].readAsNumber() if (name in members) else None)

def makeAddressCell(members, name):
    return createAddressCell(members[name].readAsAddress())

def makeAddressOfCell(members, name):
    return createAddressCell(members[name].getLocationAddress())

def makeNameCell(members, name):
    return createTextCell(getSimpleName(members, name))

def makeTaskIdCell(tcbPtr, members):
    return createTextCell(Rtx5.getDisplayableTaskId(tcbPtr, members))

def makeTaskCell(members, name):
    return makeTaskIdCell(members[name], members[name].dereferencePointer().getStructureMembers())

def makeStateCell(members):
    return createTextCell(Rtx5.getTaskState(members["state"].readAsNumber(), members))

def makeTaskWaitersCell(members, name):
    tcbPtr = members[name]
    result = []

    while nonNullPtr(tcbPtr):
        members = getPtrMemBers(tcbPtr)
        result.append(str(Rtx5.getDisplayableTaskId(tcbPtr, members)))
        tcbPtr = members["thread_next"]

    return createTextCell(', '.join(result))
    
def getSimpleName(members, name):
    member = members[name]
    location = member.resolveAddressAsString()
    index = location.find("+")
    if(index != -1):
        location = str(location)[:index]

    return location

def dereferenceThreadPointer(tcbPtr):
    return tcbPtr.dereferencePointer(Rtx5.getCType("Thread"))

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
        return Rtx5.getActiveTasks(dbg)

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
        members = threadPrev.dereferencePointer(Rtx5.getCType(self.tcbType)).getStructureMembers()

        if (members["id"].readAsNumber() == getControlBlockId(self.tcbType)):
            return [function(members, threadPrev) for function in self.functions]

        return []
