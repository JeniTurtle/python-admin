#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ipPoolAdmin
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IpPoolAdmin(Model):
    __table__ = 'ipPoolAdmin'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    uid = StringField(ddl='varchar(32)', updatable=False)
    accuracy = FloatField(default=0, ddl='float(5,4)')
    createAt = FloatField(default=time.time)
    updateAt = FloatField(default=time.time)
