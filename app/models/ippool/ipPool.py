#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ipPool
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IPPool(Model):
    __table__ = 'ipPools'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    objectId = StringField(ddl='varchar(32)', updatable=False)
    ippreId = StringField(ddl='varchar(32)', updatable=False)
    verifyType = IntegerField(default=0, nullable=True, ddl='tinyint(5)')
    authorId = StringField(updatable=False, ddl='varchar(32)')
    author = StringField(updatable=False, ddl='varchar(256)')
    status = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
    createAt = FloatField(updatable=False, default=time.time)
    updateAt = FloatField(default=time.time)
    title = StringField(updatable=False, ddl='varchar(256)')
    workType = StringField(updatable=False, ddl='varchar(256)')
    cat = StringField(updatable=False, ddl='varchar(256)')
    hasOutline = IntegerField(default=0, ddl='tinyint(1)')
    firstOldStatus = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
    secondOldStatus = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
    thirdOldStatus = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
