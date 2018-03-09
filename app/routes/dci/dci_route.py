#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import time
from conf.env import ENV
from conf.error_code import ERROR_CODE, ERROR_MESSAGE
from lib.core import get, ctx, view, interceptor
from lib.common import check_login, api, Page
from lib.utils import path_join
from lib.error import APIError

_MODULE = 'dci'

_API_HOST = {
    'production': 'http://api.yunlaiwu.com',
    'development': 'http://testapi.yunlaiwu.com:8099'
}[ENV]


def _format_data(data):
    for item in data:
        item['createAt'], item['updateAt'] = time.localtime(item['createAt']), time.localtime(item['updateAt'])
        item['createAt'] = time.strftime('%Y-%m-%d %H:%M:%S', item['createAt'])
        item['updateAt'] = time.strftime('%Y-%m-%d %H:%M:%S', item['updateAt'])


def _detail_format_data(data):
    if data.has_key('copyright') and data['copyright']:
        copy_right = {
            'super': u'全版权',
            'movie': u'电影',
            'teleplay': u'电视剧',
            'netplay': u'网剧',
            'game': u'游戏'
        }
        L = []
        for x in data['copyright'].split(","):
            if x in copy_right.keys():
                L.append(copy_right[x])

        data['copyright'] = ','.join(L)

    if data.has_key('rightownmode') and data['rightownmode']:
        data['rightownmode'] = {
            1: u'个人作品',
            2: u'合作作品'
        }[data['rightownmode']]
            
    if data.has_key('coper') and data['coper']:
        data['coper'] = json.loads(data['coper'])

    return data


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@view(path_join(_MODULE, 'list.html'))
@get(path_join(_MODULE))
def home():
    pn = int(ctx.request.get('pn', 1))
    rn = int(ctx.request.get('rn', 10))

    list_api = _API_HOST + '/copy/workchecklist?pn=%d&rn=%d&token=%s' % (pn - 1, rn, ctx.request.cookies.get('leancloud-token'))
    res_data = urllib2.urlopen(list_api)
    res = res_data.read()
    res_data.close()
    data = json.loads(res)

    if data['errno'] != 0:
        error_code = ERROR_CODE['data_exception_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    _format_data(data['data']['list'])

    page = Page(data['data']['count'], pn, rn)

    return dict(data=data['data'], page=page.to_dict(), user=ctx.request.user)


@api
@get(path_join(_MODULE, 'detail/api'))
def _detail_api():
    copy_id = ctx.request.get('copyId', False)

    if not copy_id:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    detail_api = _API_HOST + '/copy/workdetail?copyId=%s&token=%s' % (copy_id, ctx.request.cookies.get('leancloud-token'),)
    res_data = urllib2.urlopen(detail_api)
    res = res_data.read()
    res_data.close()
    data = json.loads(res)

    if data['errno'] != 0:
        error_code = ERROR_CODE['data_exception_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    return dict(data=data['data'], user=ctx.request.user)


@view(path_join(_MODULE, 'detail.html'))
@get(path_join(_MODULE, 'detail'))
def _detail():
    copy_id = ctx.request.get('copyId', False)

    if not copy_id:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    detail_api = _API_HOST + '/copy/workdetail?copyId=%s&token=%s' % (copy_id, ctx.request.cookies.get('leancloud-token'),)
    res_data = urllib2.urlopen(detail_api)
    res = res_data.read()
    res_data.close()
    data = json.loads(res)

    if data['errno'] != 0:
        error_code = ERROR_CODE['data_exception_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    return dict(data=_detail_format_data(data['data']), user=ctx.request.user, checkApi=_API_HOST + '/copy/workcheck', leancloudToken=ctx.request.cookies.get('leancloud-token'))


