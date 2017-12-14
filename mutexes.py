# Copyright (C) 2013 ARM Limited. All rights reserved.

from utils import *

class Mutexes(TCBBasedTable):

    CONTROL_BLOCK_TYPE = 3

    def __init__(self):
        id = "mutexes"

        fields = [createField(id, "addr", ADDRESS),
                  createField(id, "owner", DECIMAL),
                  createField(id, "tasks", TEXT),
                  createField(id, "priority", DECIMAL),
                  createField(id, "level", DECIMAL)]

        functions = [lambda members, prlnk: createAddressCell(prlnk.readAsAddress()),
                     lambda members, prlnk: makeTaskCell(members, "owner"),
                     lambda members, prlnk: makeTaskListCell(members, "p_lnk"),
                     lambda members, prlnk: makeNumberCell(members, "prio"),
                     lambda members, prlnk: makeNumberCell(members, "level")]

        TCBBasedTable.__init__(self, id, fields, functions, "P_MUCB", Mutexes.CONTROL_BLOCK_TYPE)
