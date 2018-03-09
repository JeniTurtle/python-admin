#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A WSGI application entry.
"""

import logging
import os

from app.routes.load_routes import load as load_routes
from conf.config import configs
from lib.core import WSGIApplication, Jinja2TemplateEngine
from lib.database import create_engine
from lib.utils import datetime_filter

logging.basicConfig(level=logging.INFO)

# init db:
create_engine(configs.database.user, configs.database.password, configs.database.database, configs.database.host)

abspath = os.path.dirname(os.path.abspath(__file__))

# init wsgi app:
wsgi = WSGIApplication(abspath)

template_engine = Jinja2TemplateEngine(os.path.join(abspath, configs.app.template))
template_engine.add_filter('datetime', datetime_filter)

wsgi.template_engine = template_engine

load_routes(wsgi)

if __name__ == '__main__':
    wsgi.run(8088, host='0.0.0.0')
