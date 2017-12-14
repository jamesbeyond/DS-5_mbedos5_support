# Copyright (C) 2013,2015 ARM Limited. All rights reserved.

from osapi import *

def getStateName(stateNames, stateVal):
    if stateVal < 0 or stateVal > (len(stateNames) -1):
        return str(stateVal)
    else:
        return stateNames[int(stateVal)]

def makeStateCell(members, stateNames, name):
    member = members[name]
    stateName = getStateName(stateNames, member.readAsNumber())

    return createTextCell(stateName)

def makeNumberCell(members, name):
    if name in members:
        return createNumberCell(members[name].readAsNumber())
    else:
        return createNumberCell(None)

def makeAddressCell(members, name):
    return createAddressCell(members[name].readAsAddress())

def makeAddressOfCell(members, name):
    return createAddressCell(members[name].getLocationAddress())

def makeTaskCell(members, name):
    memberVal = members[name]
    task = memberVal.dereferencePointer("P_TCB")
    members = task.getStructureMembers();

    return makeNumberCell(members, "task_id")

def makeTaskListCell(members, name):
    memberVal = members[name]
    result = [""]
    separator = ""

    while memberVal.readAsNumber() != 0:
        task = memberVal.dereferencePointer("P_TCB")
        members = task.getStructureMembers()
        result.append(separator)
        result.append(str(members["task_id"].readAsNumber()))
        separator = ", "
        memberVal = members["p_lnk"]

    return createTextCell(''.join(result));

# urn to int/long to hex without the irritating "L" added to the end for longs
def toHex(x):
    return "0x%X" % x

# Base class for task control block structures
class TCBBasedTable(Table):

    def __init__(self, id, fields, functions, tcbTypeName, tcbType):
        Table.__init__(self, id, fields)
        self.functions = functions
        self.tcbTypeName = tcbTypeName
        self.tcbType = tcbType

    def getRecords(self, debugSession):
        activeTCB = debugSession.evaluateExpression("os_active_TCB")
        elements = activeTCB.getArrayElements()
        records = []

        for pointer in elements:
            if pointer.readAsNumber() != 0:
                tcb = pointer.dereferencePointer("P_TCB")
                prlnk = tcb.getStructureMembers()["p_rlnk"]

                if prlnk.readAsNumber() != 0:
                    mcb = prlnk.dereferencePointer(self.tcbTypeName)
                    members = mcb.getStructureMembers();
                    cbType = members["cb_type"];

                    if cbType.readAsNumber() == self.tcbType:
                        cells = [function(members, prlnk) for function in self.functions]
                        records.append(self.createRecord(cells))

        return records
