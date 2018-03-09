#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ipSamplingVerify
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IPSamplingVerify(Model):
    __table__ = 'ipSamplingVerify'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    samplingAllotId = IntegerField(default=0, ddl='int(11)')
    verifyPerson = StringField(ddl='varchar(32)', updatable=False)
    verifyType = IntegerField(default=0, updatable=False, nullable=True, ddl='tinyint(5)')
    objectId = StringField(ddl='varchar(32)', updatable=False)
    verifyResult = IntegerField(default=0, nullable=True, ddl='tinyint(5)')
    createAt = FloatField(updatable=False, default=time.time)
    updateAt = FloatField(default=time.time)
