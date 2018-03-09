#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for ip
'''

from lib.orm import Model, StringField, FloatField, IntegerField


class IP(Model):
    __table__ = 'ip'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    createAt = FloatField(updatable=False, default=time.time)
    updateAt = FloatField(default=time.time)
