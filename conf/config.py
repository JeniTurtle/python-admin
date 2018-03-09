#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration
"""

from lib.utils import to_dict, Dict
from conf.db_conf import configs as db_conf
from conf.app_conf import configs as app_conf
from conf.session_conf import configs as session_conf

db_conf = to_dict(db_conf)
app_conf = to_dict(app_conf)
session_conf = to_dict(session_conf)

configs = Dict(database=db_conf, app=app_conf, session=session_conf)
