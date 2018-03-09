#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
common file
"""

import time
import hashlib
import functools
import json
import logging
from conf.cookie_list import LOGIN_COOKIE_NAME
from lib.core import ctx, HttpError
from error import APIPermissionError, APIError
from conf.cookie_list import LOGIN_COOKIE_KEY
from app.models.user.rms import RMS


def get_admin_auth(*args):
    auth = {
        '4_1_1': u'普通用户',
        '4_1_2': u'一评用户',
        '4_1_3': u'二评用户',
        '4_1_4': u'专家用户',
        '4_1_5': u'管理员',
        '4_1_6': u'新编剧用户',
        '4_1_7': u'新编剧管理员',
        '4_1_8': u'黑名单投票',
        '4_1_9': u'黑名单包装',
        '4_1_10': u'黑名单管理员'
    }
    L = []
    for x in args:
        if x in auth.keys():
            L.append(auth[x])

    return ','.join(L)


def check_admin():
    user = ctx.request.user
    if user and user.admin:
        return
    raise APIPermissionError('No permission.')


def dumps(obj):
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    序列化对象
    """
    return json.dumps(obj)


def api(func):
    """
    A decorator that makes a function to json api, makes the return value as json.
    将函数返回结果 转换成json 的装饰器
    @api需要对Error进行处理。我们定义一个APIError，
    这种Error是指API调用时发生了逻辑错误（比如用户不存在）
    其他的Error视为Bug，返回的错误代码为internalerror
    @app.route('/api/test')
    @api
    def api_test():
        return dict(result='123', items=[])
    """
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        try:
            r = dumps(func(*args, **kw))
        except APIError, e:
            r = json.dumps(dict(error=e.error, data=e.data, message=e.message))
        except Exception, e:
            logging.exception(e)
            r = json.dumps(dict(error='internalerror', data=e.__class__.__name__, message=e.message))
        ctx.response.content_type = 'application/json'
        return r
    return _wrapper


class Page(object):
    """
    Page object for display pages.
    """
    def __init__(self, item_count, page_index=1, page_size=15):
        """
        Init Pagination by item_count, page_index and page_size.
        :param item_count:
        :param page_index:
        :param page_size:
        """
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)
        if (item_count == 0) or (page_index < 1) or (page_index > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 0
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def to_dict(self):
        return dict(item_count=self.item_count, page_count=self.page_count, page_index=self.page_index, page_size=self.page_size, offset=self.offset, limit=self.limit)

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__


def make_signed_cookie(id, mobile, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, mobile, expires, LOGIN_COOKIE_KEY)).hexdigest()]
    print L
    return '-'.join(L)


def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = RMS.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.mobile, expires, LOGIN_COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None


def get_page_info():
    page_index = '1'
    page_size = '10'
    try:
        page_index = int(ctx.request.get('pn', page_index))
        page_size = int(ctx.request.get('rn', page_size))
    except ValueError:
        pass
    return page_index, page_size


def check_login(next):
    logging.info('try to bind user from session cookie...')
    cookie = ctx.request.cookies.get(LOGIN_COOKIE_NAME)
    ctx.request.user = None
    if cookie:
        logging.info('parse session cookie...')
        user = parse_signed_cookie(cookie)

        if user and user.id and user.stillwork == 1:
            logging.info('bind user <%s> to session...' % user.mobile)
            ctx.request.user = user
            return next()
    raise HttpError.seeother('/login')
