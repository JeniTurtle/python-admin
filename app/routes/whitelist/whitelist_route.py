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


_MODULE = 'whitelist'

_API_HOST = {
    'production': 'http://www.yunlaiwu.com',
    'development': 'http://localhost:3000'
}[ENV]


def _get_list(api_url):

    pn = int(ctx.request.get('pn', 1))
    rn = int(ctx.request.get('rn', 10))
    list_type = ctx.request.get('type', 'open')

    list_api = _API_HOST + api_url + '?listType=%s&pn=%d&rn=%d&token=%s' % (list_type, pn - 1, rn, ctx.request.cookies.get('leancloud-token'))

    res_data = urllib2.urlopen(list_api)
    res = res_data.read()
    res_data.close()
    data = json.loads(res)

    if data['code'] != 0:
        error_code = ERROR_CODE['data_exception_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    page = Page(data['count'], pn, rn)

    params = {
        'type': list_type,
        'apiHost': _API_HOST,
        'token': ctx.request.cookies.get('leancloud-token')
    }

    return dict(data=data['data'], page=page.to_dict(), param=params, user=ctx.request.user)


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


# @api
@view(path_join(_MODULE, 'list.html'))
@get(path_join(_MODULE, 'list'))
def _list():
    return _get_list('/api/tools/whiteList')


# @api
@view(path_join(_MODULE, 'agency_list.html'))
@get(path_join(_MODULE, 'agencylist'))
def _agency_list():
    return _get_list('/api/tools/whiteAgencyList')


@view(path_join(_MODULE, 'detail.html'))
@get(path_join(_MODULE, 'add'))
def _detail():
    detail_type = ctx.request.get('type', '1')
    stored_id = ctx.request.get('id')
    data = {'data': {}}

    if stored_id:
        detail_api = _API_HOST + '/api/tools/whiteList?storedIp=%s&token=%s' % (stored_id, ctx.request.cookies.get('leancloud-token'))
        res_data = urllib2.urlopen(detail_api)
        res = res_data.read()
        res_data.close()
        data = json.loads(res)

        if data['code'] != 0:
            error_code = ERROR_CODE['data_exception_error']
            raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    params = {
        'type': detail_type,
        'apiHost': _API_HOST,
        'token': ctx.request.cookies.get('leancloud-token'),
        'storedIp': stored_id or ''
    }

    return dict(data=data['data'], param=params, user=ctx.request.user)


@view(path_join(_MODULE, 'agency_detail.html'))
@get(path_join(_MODULE, 'agencyadd'))
def _agency_detail():
    stored_id = ctx.request.get('id')
    data = {'data': {}}

    if stored_id:
        detail_api = _API_HOST + '/api/tools/whiteAgencyList?storedIp=%s&token=%s' % (stored_id, ctx.request.cookies.get('leancloud-token'))
        res_data = urllib2.urlopen(detail_api)
        res = res_data.read()
        res_data.close()
        data = json.loads(res)

        if data['code'] != 0:
            error_code = ERROR_CODE['data_exception_error']
            raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    params = {
        'apiHost': _API_HOST,
        'token': ctx.request.cookies.get('leancloud-token'),
        'storedIp': stored_id or ''
    }

    return dict(data=data['data'], param=params, user=ctx.request.user)


