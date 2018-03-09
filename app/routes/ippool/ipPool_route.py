#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from app.models.ippool.ipPool import IPPool
from app.models.ipverify.ipVerify import IPVerify
from conf.error_code import ERROR_CODE, ERROR_MESSAGE
from lib.common import api, Page, get_page_info, check_login
from lib.core import get, ctx, view, interceptor, HttpError
from lib.error import APIError
from lib.utils import path_join

_MODULE = 'ippool'


def _get_list_by_page(verify_type='0', status=None, has_outline=None, title=None, order='0'):
    page_index, page_size = get_page_info()

    if title:
        args = ['%' + title + '%']
        where = 'where `title` like ? and discard = 0'
    elif status and has_outline:
        args = [verify_type, status, has_outline]
        where = 'where `verifyType` = ? and `status` = ? and `hasOutline` = ? and discard = 0'
    elif status:
        args = [verify_type, status]
        where = 'where `verifyType` = ? and `status` = ? and discard = 0'
    else:
        args = [verify_type]
        where = 'where `verifyType` = ? and discard = 0 and status != -1'

    total = IPPool.count_by(where, *args)
    page = Page(total, page_index, page_size)
    if order == '0':
        where = '%s order by createAt DESC limit ?,?' % (where,)
    else:
        where = '%s order by updateAt DESC limit ?,?' % (where,)
    args.append(page.offset)
    args.append(page.limit)
    lists = IPPool.find_by(where, *args)

    return lists, page.to_dict()


def _get_excellent_list_by_page(title, order):
    page_index, page_size = get_page_info()
    if title:
        args = ['%' + title + '%']
        where = 'where `title` like ? and discard = 0'
    else:
        args = []
        where = 'where (`verifyType` = 3 or `verifyType` = 4) and discard = 0 and status = 1'

    total = IPPool.count_by(where, *args)
    page = Page(total, page_index, page_size)
    if order == '0':
        where = '%s order by createAt DESC limit ?,?' % (where,)
    else:
        where = '%s order by updateAt DESC limit ?,?' % (where,)
    args.append(page.offset)
    args.append(page.limit)
    lists = IPPool.find_by(where, *args)
    return lists, page.to_dict()


def _format_data(data):
    for item in data:
        item.createAt, item.updateAt = time.localtime(item.createAt), time.localtime(item.updateAt)
        item.createAt = time.strftime('%Y-%m-%d %H:%M:%S', item.createAt)
        item.updateAt = time.strftime('%Y-%m-%d %H:%M:%S', item.updateAt)

        if not hasattr(item, 'verifyType') or not hasattr(item, 'status'):
            continue

        if item.verifyType == 0:
            item.result = u'一评待分配'
        elif item.verifyType == 1 and item.status == 0:
            item.result = u'一评待评审'
        elif item.verifyType == 1 and item.status == 1:
            item.result = u'一评通过'
        elif item.verifyType == 1 and item.status == 2:
            item.result = u'一评不通过'
        elif item.verifyType == 3 and item.status == 0:
            item.result = u'二评待评审'
        elif item.verifyType == 3 and item.status == 1:
            item.result = u'二评通过'
        elif item.verifyType == 3 and item.status == 2:
            item.result = u'二评不通过'
        elif item.verifyType == 4 and item.status == 0:
            item.result = u'二评复审待评审'
        elif item.verifyType == 4 and item.status == 1:
            item.result = u'二评复审通过'
        elif item.verifyType == 4 and item.status == 2:
            item.result = u'二评复审不通过'
        else:
            item.result = u'错误状态'


def _get_ippool_list():
    verify_type = ctx.request.get('verifyType', '1')
    status = ctx.request.get('status', None)
    has_outline = ctx.request.get('hasOutline', None)
    title = ctx.request.get('title', None)
    order = ctx.request.get('order', '0')

    if ctx.request.user.crm.find('4_1_5') == -1:
        lists, page = _get_excellent_list_by_page(title, order)
    else:
        lists, page = _get_list_by_page(verify_type, status, has_outline, title, order)

    param = {
        'verifyType': verify_type,
        'status': status,
        'hasOutline': has_outline,
        'title': title if title else '',
    }
    _format_data(lists)
    return dict(page=page, list=lists, param=param, user=ctx.request.user)


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@view(path_join(_MODULE, 'ippool_list.html'))
@get(path_join(_MODULE))
def ip_list():
    return _get_ippool_list()


@api
@get(path_join(_MODULE, '/api/list'))
def api_ip_list():
    return _get_ippool_list()


@api
@get(path_join(_MODULE, '/api/verifyResult'))
def api_verify_result():
    object_id = ctx.request.get('objectId')

    if not object_id:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    first_res = IPVerify.find_by('where verifyType = 1 and objectId = ? order by updateAt ASC', object_id)
    second_res = IPVerify.find_by('where verifyType = 3 and objectId = ? order by updateAt ASC', object_id)
    third_res = IPVerify.find_by('where verifyType = 4 and objectId = ? order by updateAt ASC', object_id)
    _format_data(first_res), _format_data(second_res), _format_data(third_res)

    return dict(first=first_res, second=second_res, third=third_res)



