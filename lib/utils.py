#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import uuid
import urllib
from datetime import datetime

"""
utils
"""


class Dict(dict):
    """
    字典对象
    实现一个简单的可以通过属性访问的字典，比如 x.key = value
    """
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def next_id(t=None):
    """
    生成一个唯一id   由 当前时间 + 随机数（由伪随机数得来）拼接得到
    :param t: unix时间戳， 默认为None
    :return: 长度为50的字符串
    """
    t = t is None and time.time() or t
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


def to_unicode(s, encoding='utf-8'):
    """
    unicode转码
    :param s: str
    :param encoding:
    :return:
    """
    return s.decode('utf-8')


def quote(s, encoding='utf-8'):
    """
    url转义
    :param s:
    :param encoding:
    :return:
    """
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return urllib.quote(s)


def unquote(s, encoding='utf-8'):
    """
    url反转义
    :param s:
    :param encoding:
    :return:
    """
    return urllib.unquote(s).decode(encoding)


def to_str(s):
    """
    字符串转换
    :param s:
    :return:
    """
    if isinstance(s, str):
        return s
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return str(s)


def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


def merge(defaults, override):
    """
    合并override 和 default 配置文档，返回字典
    """
    r = {}
    for k, v in defaults.iteritems():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


def to_dict(d):
    """
    将一个字典对象转换成 一个Dict对象
    """
    D = Dict()
    for k, v in d.iteritems():
        D[k] = to_dict(v) if isinstance(v, dict) else v
    return D


def path_join(*args):
    l = ['']
    for x in args:
        if not isinstance(x, str):
            raise TypeError('path name is not a string')
        x = x if x[0] != '/' else x[1:]
        l.append(x)

    return '/'.join(l)
