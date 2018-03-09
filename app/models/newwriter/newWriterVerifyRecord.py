#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for newWriterVerifyRecord
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class NewWriterVerifyRecord(Model):
    __table__ = 'newWriterVerifyRecord'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    uid = StringField(ddl='varchar(32)', updatable=False)
    newWriterId = IntegerField(ddl='int(11)', updatable=False)
    story = IntegerField(default=0, ddl='int(5)')
    structure = IntegerField(default=0, ddl='int(5)')
    character = IntegerField(default=0, ddl='int(5)')
    market = IntegerField(default=0, ddl='int(5)')
    status = IntegerField(default=0, nullable=True, ddl='tinyint(2)')
    createAt = FloatField(updatable=False, default=time.time)
    updateAt = FloatField(default=time.time)
