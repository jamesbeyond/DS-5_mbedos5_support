# Copyright (C) 2013 ARM Limited. All rights reserved.

from utils import *

MAILBOX_STATE_NAMES = ["NOT_WAITING",       # 0
                       "WAITING_GET",       # 1
                       "WAITING_SEND",      # 2
                       "WAITING_ALLOCATE"]  # 3


class Mailboxes(TCBBasedTable):

    CONTROL_BLOCK_TYPE = 1

    def __init__(self):
        id = "mailboxes"

        fields = [createField(id, "addr", ADDRESS),
                  createField(id, "tasks", TEXT),
                  createField(id, "state", TEXT),
                  createField(id, "first", DECIMAL),
                  createField(id, "last", DECIMAL),
                  createField(id, "count", DECIMAL),
                  createField(id, "size", DECIMAL),
                  createField(id, "messages", ADDRESS)]

        functions = [lambda members, prlnk: createAddressCell(prlnk.readAsAddress()),
                     lambda members, prlnk: makeTaskListCell(members, "p_lnk"),
                     lambda members, prlnk: makeStateCell(members, MAILBOX_STATE_NAMES, "state"),
                     lambda members, prlnk: makeNumberCell(members, "first"),
                     lambda members, prlnk: makeNumberCell(members, "last"),
                     lambda members, prlnk: makeNumberCell(members, "count"),
                     lambda members, prlnk: makeNumberCell(members, "size"),
                     lambda members, prlnk: makeAddressOfCell(members, "msg")]

        TCBBasedTable.__init__(self, id, fields, functions, "P_MCB", Mailboxes.CONTROL_BLOCK_TYPE)
