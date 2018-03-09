#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for newWriterPool
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class NewWriterPool(Model):
    __table__ = 'newWriterPool'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    ippreId = StringField(ddl='varchar(32)', updatable=False)
    uid = StringField(ddl='varchar(32)', updatable=False)
    type = IntegerField(default=0, updatable=True, ddl='tinyint(5)')
    phone = StringField(ddl='varchar(32)', updatable=False)
    verifyAdmin = StringField(ddl='text')
    status = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
    oldStatus = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
    result = IntegerField(default=0.00, nullable=True, ddl='float(5,2)')
    finalState = IntegerField(default=0, updatable=False, nullable=True, ddl='tinyint(5)')
    createAt = FloatField(updatable=False, default=time.time)
    updateAt = FloatField(default=time.time)
