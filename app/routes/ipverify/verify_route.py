#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from app.models.ippool.ipPool import IPPool
from app.models.ipverify.ipVerify import IPVerify
from lib.common import api, Page, get_page_info, check_login
from lib.core import get, ctx, view, interceptor, HttpError
from lib.utils import path_join
from lib.error import APIError
from conf.error_code import ERROR_CODE, ERROR_MESSAGE

_MODULE = 'ipverify'


def _get_list_by_page(verify_type='0', verify_result=None, has_outline=None, title=None, order='0'):
    page_index, page_size = get_page_info()
    join = 'as a left join %s as b on a.objectId = b.objectId where b.discard = 0' % (IPPool.__table__,)

    if title:
        args = ['%' + title + '%', ctx.request.user.uid]
        where = '%s and b.title like ? and a.adminId = ?' % (join,)
    elif verify_result and has_outline:
        args = [verify_type, verify_result, has_outline, ctx.request.user.uid]
        where = '%s and a.verifyType = ? and a.verifyResult = ? and b.hasOutline = ? and a.adminId = ?' % (join,)
    elif verify_result:
        args = [verify_type, verify_result, ctx.request.user.uid]
        where = '%s and a.verifyType = ? and a.verifyResult = ? and a.adminId = ?' % (join,)
    else:
        args = [verify_type, ctx.request.user.uid]
        where = '%s and a.verifyType = ? and a.adminId = ?' % (join,)

    total = IPVerify.count_by_field(where, 'a.id', *args)
    page = Page(total, page_index, page_size)
    if order == '1':
        where = '%s order by a.updateAt DESC limit ?,?' % (where,)
    else:
        where = '%s order by b.createAt ASC limit ?,?' % (where,)

    args.append(page.offset)
    args.append(page.limit)
    lists = IPVerify.select_by(where, args, ['a.*', 'b.title', 'b.hasOutline', 'b.author', 'b.createAt as publishTime'])

    return lists, page.to_dict()


def _get_verify_list():
    verify_type = ctx.request.get('verifyType', '1')
    verify_result = ctx.request.get('verifyResult', None)
    has_outline = ctx.request.get('hasOutline', None)
    title = ctx.request.get('title', None)
    order = ctx.request.get('order', '0')

    lists, page = _get_list_by_page(verify_type, verify_result, has_outline, title, order)
    param = {
        'verifyType': verify_type,
        'verifyResult': verify_result,
        'hasOutline': has_outline,
        'title': title if title else '',
    }
    _format_data(lists)
    return dict(page=page, list=lists, param=param, user=ctx.request.user)


def _format_data(data):
    for item in data:
        item.createAt, item.updateAt = time.localtime(item.createAt), time.localtime(item.updateAt)
        item.publishTime = time.localtime(item.publishTime)
        item.createAt = time.strftime('%Y-%m-%d %H:%M:%S', item.createAt)
        item.updateAt = time.strftime('%Y-%m-%d %H:%M:%S', item.updateAt)
        item.publishTime = time.strftime('%Y-%m-%d %H:%M:%S', item.publishTime)


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@view(path_join(_MODULE, 'verify_list.html'))
@get(path_join(_MODULE))
def ip_list():
    return _get_verify_list()


@api
@get(path_join(_MODULE, '/api/list'))
def api_verify_list():
    return _get_verify_list()


@api
@get(path_join(_MODULE, '/api/verify'))
def api_verify():
    verify_type = ctx.request.get('verifyType', None)
    object_id = ctx.request.get('objectId', None)
    verify_result = ctx.request.get('verifyResult', None)

    if not ctx.request.user.uid:
        raise HttpError.seeother('/login')

    # 如果缺少verify_type，或者object_id，或者verifyResult不等于1或2那么抛出参数错误
    if not verify_type or not object_id or (verify_result != '1' and verify_result != '2'):
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    # 先查一次，看看这个ip是否有效，并且是否被评审过了，如果已经评审了，那么不能修改结果
    where = 'where `objectId` = ? and `adminId` = ? and `verifyType` = ?'
    verify_data = IPVerify.select_by(where, [object_id, ctx.request.user.uid, verify_type], ['verifyResult'])

    if not verify_data or 'verifyResult' not in verify_data[0] or verify_data[0].verifyResult != 0:
        error_code = ERROR_CODE['not_allow_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    # 如果是未评审过的，那么可以放心大胆的修改状态了
    ip_verify = IPVerify(verifyResult=verify_result, updateAt=time.time())
    res = ip_verify.update_by(where, object_id, ctx.request.user.uid, verify_type)

    # 判断下返回的结果是不是存在问题，好安心执行下面的操作
    if not hasattr(res, 'verifyResult') or res.verifyResult != verify_result:
        error_code = ERROR_CODE['update_sql_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    # 获取其他人的评审记录
    select_where = 'where `objectId` = ? and `adminId` != ? and `verifyType` = ?'
    verify_list = IPVerify.find_by(select_where, object_id, ctx.request.user.uid, verify_type)

    pass_count, not_pass_count = 0, 0

    if verify_result == '1':
        pass_count += 1
    else:
        not_pass_count += 1

    for item in verify_list:
        if item.verifyResult == 0:
            # 如果有没评审完的人，那么停止操作，返回上面的更新结果
            return res
        elif item.verifyResult == 1:
            pass_count += 1
        else:
            not_pass_count += 1

    # 计算下多人的评审结果，顺便将ipPools表的状态也改一下
    old_status_field = {
        '1': 'firstOldStatus',
        '3': 'secondOldStatus',
        '4': 'thirdOldStatus'
    }[verify_type]
    final_result = 1 if pass_count > not_pass_count else 2
    field = {
        'status': final_result,
        old_status_field: final_result,
        'updateAt': time.time()
    }

    where = 'where objectId = ? and verifyType = ?'
    update_info = IPPool(**field).update_by(where, object_id, verify_type)
    res.ipPoolsInfo = update_info
    return res

