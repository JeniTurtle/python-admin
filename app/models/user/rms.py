#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models for rms
"""

from lib.orm import Model, StringField, IntegerField


class RMS(Model):
    __table__ = 'rms'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    name = StringField(ddl='varchar(256)')
    uid = StringField(ddl='varchar(32)')
    mobile = StringField(ddl='varchar(32)')
    stillwork = IntegerField(default=0, ddl='int(4)')
    crm = StringField(ddl='varchar(256)')
