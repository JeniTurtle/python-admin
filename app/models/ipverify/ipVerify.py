#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ipVerify
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IPVerify(Model):
    __table__ = 'ipVerify'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    objectId = StringField(ddl='varchar(32)', updatable=False)
    ipAllotId = IntegerField(default=0, updatable=False, ddl='int(11)')
    verifyType = IntegerField(default=0, updatable=False, nullable=True, ddl='tinyint(5)')
    adminId = StringField(ddl='varchar(32)', updatable=False)
    username = StringField(ddl='varchar(256)', updatable=False)
    verifyResult = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
    createAt = FloatField(updatable=False, default=time.time)
    updateAt = FloatField(default=time.time)
