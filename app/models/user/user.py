#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models for user
"""

from lib.orm import Model, StringField, IntegerField


class User(Model):
    __table__ = 'user'

    id = IntegerField(primary_key=True, default=0, ddl='int(11)')
    username = StringField(ddl='text')
    person_nickname = StringField(ddl='text')
    mobilePhoneNumber = StringField(ddl='varchar(64)')
