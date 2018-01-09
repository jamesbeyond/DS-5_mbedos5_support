# Copyright (C) 2013,2015 ARM Limited. All rights reserved.

from utils import *
from contexts import TASK_STATE_NAMES

class Tasks(Table):

    CONTROL_BLOCK_TYPE = 0

    def __init__(self):
        id = "tasks"
        fields = [createPrimaryField(id, "id", DECIMAL),
                  createField(id, "name", TEXT),
                  createField(id, "priority", DECIMAL),
                  createField(id, "state", TEXT),
                  createField(id, "delay", DECIMAL),
                  createField(id, "mask", HEXADECIMAL),
                  createField(id, "flags", DECIMAL),
                  createField(id, "waiting", TEXT)]
        Table.__init__(self, id, fields)

    def readTask(self, taskControlBlock, debugger):
        members = taskControlBlock.getStructureMembers();

        cells = [makeNumberCell(members, "id"),
                 makeNameCell(members, "name"),
                 makeNumberCell(members, "priority"),
                 makeStateCell(members, TASK_STATE_NAMES, "state"),
                 makeDelayCell(members),
                 makeNumberCell(members, "context"),
                 makeNumberCell(members, "wait_flags"),
                 makeControlBlockCell(members, "thread_prev", debugger)                 ]

        return self.createRecord(cells)

    def getRecords(self, debugSession):
        idleTCB = debugSession.evaluateExpression("_main_obj")
        records = [self.readTask(idleTCB, debugSession)]

        # activeTCB = debugSession.evaluateExpression("_main_stack")
        # elements = activeTCB.getArrayElements()

        # for pointer in elements:
            # if pointer.readAsNumber() != 0:
                # record = self.readTask(pointer.dereferencePointer("P_TCB"), debugSession)
                # records.append(record)

        return records

CONTROL_BLOCK_NAMES = ["TASK",       # 0
                       "MAILBOX",    # 1
                       "SEMAPHORE",  # 2
                       "MUTEX" ]     # 3

def makeDelayCell(members):
     # mbedos5 stores delayed tasks in an doubly linked list ordered by ascending expiry
     # time, starting with the task pointed to by the global os_dly variable. Each task
     # in the list has its delta_time member set to the number of milliseconds until the
     # *next* task in the list is due to expire. To calculate the delay for a given task
     # it is required to sum the delta_time members of all previous tasks in the delay list.
    delayListPtr = members["thread_next"]
    delay = 0

    while (delayListPtr.readAsNumber() != 0):
        previous = delayListPtr.dereferencePointer()
        previousMembers = previous.getStructureMembers()
        delay += previousMembers["delay"].readAsNumber()
        delayListPtr = previousMembers["thread_next"]

    if (delay > 0):
        cell = createNumberCell(delay)
    else:
        # Not relevant so no data in this cell
        cell = createNumberCell(None)

    return cell

def makeNameCell(members, name):
    member = members[name]
    location = member.resolveAddressAsString()
    index = location.find("+")
    if(index != -1):
        location = str(location)[0:index]
    return createTextCell(location)

def makeControlBlockCell(members, name, debugger):
    pointerToControlBlock = members[name]
    if (pointerToControlBlock.readAsNumber() == 0):
        return createTextCell("")
    memberVal = pointerToControlBlock.dereferencePointer("P_TCB")
    members = memberVal.getStructureMembers()
    memberVal = members["attr"]
    controlBlockStateVal = memberVal.readAsNumber()
    if controlBlockStateVal == Tasks.CONTROL_BLOCK_TYPE:
        return makeControlBlockCell(members, name, debugger)

    controlBlockName = ""
    if(controlBlockStateVal > 0 and controlBlockStateVal < (len(CONTROL_BLOCK_NAMES))):
        controlBlockName = CONTROL_BLOCK_NAMES[int(controlBlockStateVal)] + "@" + str(pointerToControlBlock.readAsAddress())

    return createTextCell(controlBlockName)
