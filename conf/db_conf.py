#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Default database configurations.
"""

import env

configs = {
    'development': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '111111',
        'database': 'pyadmin'
    },
    'production': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'www-data',
        'password': 'www-data',
        'database': 'awesome'
    }
}[env.ENV]
