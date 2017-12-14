# Copyright (C) 2013 ARM Limited. All rights reserved.

from utils import *

class Semaphores(TCBBasedTable):

    CONTROL_BLOCK_TYPE = 2

    def __init__(self):
        id = "semaphores"

        fields = [createField(id, "addr", ADDRESS),
                  createField(id, "tokens", DECIMAL),
                  createField(id, "tasks", TEXT)]

        functions = [lambda members, prlnk: createAddressCell(prlnk.readAsAddress()),
                     lambda members, prlnk: makeNumberCell(members, "tokens"),
                     lambda members, prlnk: makeTaskListCell(members, "p_lnk")]

        TCBBasedTable.__init__(self, id, fields, functions, "P_SCB", Semaphores.CONTROL_BLOCK_TYPE)
