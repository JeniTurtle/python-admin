#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ipSamplingAllot
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IPSamplingAllot(Model):
    __table__ = 'ipSamplingAllot'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    owner = StringField(ddl='varchar(32)', updatable=False)
    allotNum = IntegerField(default=0, ddl='int(11)')
    accuracy = FloatField(ddl='float(5,4)')
    createAt = FloatField(updatable=False, default=time.time)
    updateAt = FloatField(default=time.time)
