#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ipBlacklist
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IPBlacklist(Model):
    __table__ = 'ipBlacklist'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    objectId = StringField(ddl='varchar(32)')
    packagerId = StringField(ddl='varchar(32)')
    operatorId = StringField(ddl='varchar(32)')
    batch = IntegerField(default=0, ddl='int(10)')
    title = StringField(ddl='varchar(256)')
    voteTurnout = FloatField(ddl='float(5,4)')
    status = IntegerField(default=0, ddl='tinyint(10)')
    voteEnd = IntegerField(default=0, ddl='tinyint(1)')
    isShortcut = IntegerField(default=0, ddl='tinyint(1)')
    uptime = IntegerField(default=0, ddl='int(11)')
    blacklistUpdateAt = FloatField(default=time.time())
    createAt = FloatField(updatable=False, default=time.time())
    updateAt = FloatField(default=time.time())