# Copyright (C) 2013,2015 ARM Limited. All rights reserved.

from utils import *

class System(Table):

    def __init__(self):
        id = "system"
        fields = [createField(id, "item", TEXT), createField(id, "value", TEXT)]
        Table.__init__(self, id, fields)

    def getRecords(self, debugSession):
        clockrate = debugSession.evaluateExpression("osRtxConfig.tick_freq").readAsNumber()
        # stackinfo = debugSession.evaluateExpression("os_stackinfo").readAsNumber()
        os_stack_sz = debugSession.evaluateExpression("osRtxConfig.thread_stack_size").readAsNumber()
        timeout = debugSession.evaluateExpression("osRtxConfig.robin_timeout").readAsNumber()

        records = [self.buildRecord("system.record.clockrate", clockrate)]
        # records.append(self.buildRecord("system.record.default_stack_info", toHex(stackinfo & 0xFFFF)))
        records.append(self.buildRecord("system.record.timeout", timeout))
        # records.append(self.buildRecord("system.record.private_stack_info", ((stackinfo >> 16) & 0xFF)))
        records.append(self.buildRecord("system.record.total_private_stack", toHex(os_stack_sz)))
        # records.append(self.buildRecord("system.record.stack_overflow_check", self.getStackOverflowCheck(stackinfo)))
        # records.append(self.buildRecord("system.record.task_usage", self.getTaskUsage(debugSession)))
        # records.append(self.buildRecord("system.record.user_timers", self.getUserTimers(debugSession)))

        return records

    def buildRecord(self, item, value):
        return self.createRecord([createTextCell(item), createTextCell(str(value))])

    # def getStackOverflowCheck(self, stackinfo):
        # if ((stackinfo >> 24) != 0):
            # return "system.stack_overflow_check.yes"
        # else:
            # return "system.stack_overflow_check.no"

    # def getTaskUsage(self, debugSession):
        # activeTCB = debugSession.evaluateExpression("os_active_TCB")
        # activeTasks = 0
        # elements = activeTCB.getArrayElements()
        # for element in elements:
            # if (element.readAsNumber() != 0):
                # activeTasks = activeTasks + 1
        # return "system.task_usage.description" + Localiser.FORMAT_SEPARATOR + str(len(elements)) + Localiser.FORMAT_SEPARATOR + str(activeTasks)

    # def getUserTimers(self, debugSession):
        # timerList = debugSession.evaluateExpression("os_timer_head")
        # count = 0

        # while timerList.readAsNumber() != 0:
            # element = timerList.dereferencePointer().getStructureMembers()
            # timerList = element["next"]
            # count = count + 1

        # return count
