#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

'''
Models for users
'''

from lib.utils import next_id
from lib.orm import Model, StringField, BooleanField, FloatField


class Users(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(updatable=False, ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(updatable=False, default=time.time)
