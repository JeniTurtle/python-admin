#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import leancloud
from lib.core import get, ctx, view, interceptor, HttpError
from lib.common import api, Page, get_page_info, check_login
from lib.utils import path_join
from app.models.user.user import User
from app.models.user.rms import RMS
from app.models.ippool.ipPool import IPPool
from app.models.newwriter.newWriterPool import NewWriterPool
from app.models.newwriter.newWriterVerifyRecord import NewWriterVerifyRecord
from lib.error import APIError
from conf.error_code import ERROR_CODE, ERROR_MESSAGE

_MODULE = 'newwriter'

leancloud.init("2eYaD9YTijEC4iPaOoMWqtVK", "54f0pbF9pbbBGi4wFQTItUeQ")
IPPRE = leancloud.Object.extend('IPPRE')


def _format_data(data):
    global IPPRE
    query = IPPRE.query
    
    for item in data:
        item.createAt, item.updateAt = time.localtime(item.createAt), time.localtime(item.updateAt)
        item.createAt = time.strftime('%Y-%m-%d %H:%M:%S', item.createAt)
        item.updateAt = time.strftime('%Y-%m-%d %H:%M:%S', item.updateAt)

        try:
            print item.ippreId
            query_result = query.get(item.ippreId)
            item.ippreTitle = query_result.get('title')
            item.ippreStatus = query_result.get('status')
            item.rawFile = query_result.get('rawFile')
        except:
            item.ippreTitle = '查询出错'
            item.ippreStatus = '9999'
            item.rawFile = None


def _get_list_by_page(list_type='0', status='-1', final_state='-1', title=None, boutique='-1'):
    page_index, page_size = get_page_info()

    args = [list_type]
    where = 'where type = ?'

    if title:
        global IPPRE
        query = IPPRE.query

        query_res = query.contains('title', title).find()

        id_list = []
        for info in query_res:
            id_list.append(info.id)

        args = []
        where = "where ippreId in ('%s')" % ("','".join(id_list),)

    else:
        if status != '-1':
            args.append(status)
            where = '%s and status = ?' % (where,)
        if final_state != '-1':
            args.append(final_state)
            where = '%s and finalState = ?' % (where,)
        if boutique == '1':
            where = '%s and ((verifyType = 3 or verifyType = 4) and verifyResult = 1)' % (where,)
        if boutique == '2':
            where = '%s and ((verifyType = 3 or verifyType = 4) and verifyResult = 2)' % (where,)
        if boutique == '3':
            where = '%s and ((verifyType = 1 and verifyResult = 1) or ((verifyType = 3 or verifyType = 4) and verifyResult = 0))' % (where,)
        if boutique == '4':
            where = '%s and verifyType = 1 and verifyResult = 2' % (where,)

    total = NewWriterPool.count_by(where, *args)

    page = Page(total, page_index, page_size)
    where = '%s order by id DESC limit ?,?' % (where,)

    args.append(page.offset)
    args.append(page.limit)
    lists = NewWriterPool.find_by(where, *args)
    IPPool.join_by(lists, 'ippreId', 'ippreId')
    User.join_by(lists, 'uid', 'id')

    return lists, page.to_dict()


def _get_verify_result(newwriter_id):
    args = [newwriter_id]
    where = 'where newWriterId = ?'
    res = NewWriterVerifyRecord.find_by(where, *args)
    RMS.join_by(res, 'uid', 'uid')
    return res


def _get_verify_list(status=None):
    page_index, page_size = get_page_info()

    join = 'as a left join %s as b on a.newWriterId = b.id' % (NewWriterPool.__table__,)
    args = [ctx.request.user.uid]
    where = '%s where a.uid = ? and a.status != 1' % (join,)
    count_where = 'where uid = ? and status != 1'

    if status is not None:
        args.append(status)
        where = '%s and a.status = ?' % (where,)
        count_where = '%s and status = ?' % (count_where,)

    total = NewWriterVerifyRecord.count_by(count_where, *args)
    page = Page(total, page_index, page_size)

    where = '%s order by a.updateAt DESC limit ?,?' % (where,)

    args.append(page.offset)
    args.append(page.limit)
    lists = NewWriterVerifyRecord.select_by(where, args, ['a.*', 'b.phone', 'b.ippreId', 'b.uid as userId', 'b.verifyType', 'b.verifyResult'])
    IPPool.join_by(lists, 'ippreId', 'ippreId')
    User.join_by(lists, 'userId', 'id')

    return lists, page.to_dict()


def _allot_method(ip_list, admin_list, everyone_num):
    admins = []

    for admin in admin_list:
        temp = {
            'uid': admin,
            'verifyList': []
        }
        admins.append(temp)

    for ip in ip_list:
        index = 0
        admins = sorted(admins, key=lambda x: len(x['verifyList']))

        for admin in admins:
            if index >= everyone_num:
                continue

            if ip not in admin['verifyList']:
                admin['verifyList'].append(ip)
            else:
                continue
            index += 1
    return admins


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@interceptor(path_join(_MODULE))
def check_auth_interceptor(next):
    if ctx.request.user.crm.find('4_1_6') == -1 and ctx.request.user.crm.find('4_1_7') == -1:
        raise HttpError.seeother('/home')

    return next()


@view(path_join(_MODULE, 'newwriter_list.html'))
@get(path_join(_MODULE))
def newwriter_list():
    list_type = ctx.request.get('type', '0')
    status = ctx.request.get('status', '-1')
    final_state = ctx.request.get('finalState', '-1')
    boutique = ctx.request.get('boutique', '-1')
    title = ctx.request.get('title', None)
    lists, page = _get_list_by_page(list_type, status, final_state, title, boutique)

    param = {
        'type': list_type,
        'status': status,
        'finalState': final_state,
        'title': title if title else '',
        'boutique': boutique,
        'token': ctx.request.cookies.get('leancloud-token'),
    }

    _format_data(lists)
    return dict(page=page, list=lists, param=param, user=ctx.request.user)


@view(path_join(_MODULE, 'verify_list.html'))
@get(path_join(_MODULE, '/verifyList'))
def verify_list():
    status = ctx.request.get('status', None)
    status = status if status == '-1' or status == '0' else None

    lists, page = _get_verify_list(status)

    param = {
        'status': status,
    }

    _format_data(lists)

    return dict(page=page, list=lists, param=param, user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/list'))
def api_newwriter_list():
    list_type = ctx.request.get('type', '0')
    status = ctx.request.get('status', '-1')
    final_state = ctx.request.get('finalState', '-1')
    boutique = ctx.request.get('boutique', '-1')
    title = ctx.request.get('title', None)
    lists, page = _get_list_by_page(list_type, status, final_state, title, boutique)

    param = {
        'type': list_type,
        'status': status,
        'finalState': final_state,
        'title': title if title else '',
        'boutique': boutique,
        'token': ctx.request.cookies.get('leancloud-token'),
    }

    _format_data(lists)
    return dict(page=page, list=lists, param=param, user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/verifyResult'))
def api_verify_result():
    newwriter_id = ctx.request.get('newWriterId', None)

    if not newwriter_id:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    res = _get_verify_result(newwriter_id)

    param = {
        'newWriterId': newwriter_id,
    }

    return dict(list=res, param=param, user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/verifyList'))
def api_verify_list():
    status = ctx.request.get('status', None)
    status = status if status == '-1' or status == '0' else None

    lists, page = _get_verify_list(status)

    param = {
        'status': status,
    }

    _format_data(lists)

    return dict(page=page, list=lists, param=param, user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/allot'))
def api_allot():
    if ctx.request.user.crm.find('4_1_7') == -1:
        error_code = ERROR_CODE['not_allow_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    ip_list = ctx.request.get('ipList', '')
    admin_list = ctx.request.get('adminList', '')
    everyone_num = int(ctx.request.get('everyoneNum', 0))

    ip_list = ip_list.split(',')
    admin_list = admin_list.split(',')

    admins = _allot_method(ip_list, admin_list, everyone_num)

    try:
        for admin in admins:
            for newwriter_id in admin['verifyList']:
                field = {
                    'uid': admin['uid'],
                    'newWriterId': newwriter_id,
                    'createAt': time.time(),
                    'updateAt': time.time(),
                    'status': -1
                }
                NewWriterVerifyRecord(**field).insert()
    except:
        error_code = ERROR_CODE['insert_sql_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    update_field = {'type': 1, 'status': 0}

    new_ip_list = []
    for ip in ip_list:
        new_ip_list.append(str(int(ip)))

    NewWriterPool(**update_field).update_by('where id in (%s)' % (','.join(new_ip_list),))

    return dict(error=0)


@api
@get(path_join(_MODULE, '/api/verify'))
def api_verify():
    newwriter_id = ctx.request.get('newWriterId', None)
    story = int(ctx.request.get('story', 0))
    structure = int(ctx.request.get('structure', 0))
    character = int(ctx.request.get('character', 0))
    market = int(ctx.request.get('market', 0))

    if not newwriter_id:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    args = [
        newwriter_id,
        ctx.request.user.uid
    ]
    NewWriterVerifyRecord(status=0, story=story, structure=structure, character=character, market=market).update_by('where newWriterId = ? and uid = ?', *args)
    res = NewWriterVerifyRecord.find_by('where newWriterId = ? and uid != ?', *args)

    count, state = (story + structure + character + market), True
    for info in res:
        if info.status == -1:
            state = False
            break
        count += (info.story + info.structure + info.character + info.market)

    if state:
        count /= (len(res) + 1)
        NewWriterPool(id=newwriter_id, status=1, result=count).update()

    return dict(error=0)
