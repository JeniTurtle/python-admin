#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ipBlacklistVote
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IPBlacklistVote(Model):
    __table__ = 'ipBlacklistVote'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    ipId = IntegerField(default=0, ddl='int(11)')
    voterId = StringField(ddl='varchar(32)', updatable=False)
    voterName = StringField(ddl='varchar(128)')
    result = IntegerField(default=0, ddl='tinyint(5)')
    reason = StringField(ddl='varchar(1024)')
    createAt = FloatField(updatable=False, default=time.time())
    updateAt = FloatField(default=time.time())