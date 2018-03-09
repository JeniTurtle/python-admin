#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from app.models.user.rms import RMS
from app.models.ippool.ipStatis import IPStatis
from app.models.ippool.ip import IP
from app.models.blacklist.ipBlacklist import IPBlacklist
from app.models.blacklist.ipBlacklistVote import IPBlacklistVote
from conf.error_code import ERROR_CODE, ERROR_MESSAGE
from lib.core import get, post, ctx, view, interceptor, HttpError
from lib.common import check_login, api, get_page_info, Page
from lib.error import APIError
from lib.utils import path_join

_MODULE = 'blacklist'


def _get_votelist(is_admin=False):
    batch = ctx.request.get('batch', None)
    title = ctx.request.get('title', None)

    batch_list = IPBlacklist.select_by('where batch > 0 group by batch order by batch DESC', [], ['batch'])

    if not batch and len(batch_list) > 0:
        batch = batch_list[0].batch

    param = {
        'batchList': batch_list,
        'batch': "" if not batch else batch,
        'title': title if title else '',
    }

    lists = []
    if not not batch:
        where = 'where `batch` = ? order by voteEnd DESC'
        lists = IPBlacklist.find_by(where, batch)
        IP.join_by(lists, 'id', 'id')

        if not is_admin:
            where = 'where voterId = "%s"' % (ctx.request.user.uid,)
            IPBlacklistVote.join_by(lists, 'id', 'ipId', where)
            lists = sorted(lists, key=lambda x: x.ip.pagerankVal, reverse=True)
        else:
            lists = sorted(lists, key=lambda x: x.voteTurnout, reverse=True)

    _format_data(lists)
    return dict(list=lists, param=param, user=ctx.request.user)


def _get_blacklist_by_page(title, status, order):
    page_index, page_size = get_page_info()

    if title:
        args = ['%' + title + '%']
        where = 'where `title` like ?'
    else:
        args = [status]
        where = 'where status = ?'

    total = IPBlacklist.count_by(where, *args)
    page = Page(total, page_index, page_size)

    if status < 3:
        order_field = 'updateAt ASC'
    else:
        order_field = 'blacklistUpdateAt DESC'

    where = '%s order by %s limit ?,?' % (where, order_field)
    args.append(page.offset)
    args.append(page.limit)
    lists = IPBlacklist.find_by(where, *args)

    if status > 1:
        RMS.join_by(lists, 'packagerId', 'uid')

    IP.join_by(lists, 'id', 'id')
    IPStatis.join_by(lists, 'id', 'ipId')
    return lists, page.to_dict()


def _get_package_list_by_page(title, status, order):
    page_index, page_size = get_page_info()

    args = [ctx.request.user.uid]
    where = "where packagerId = ?"

    if title:
        args.append('%' + title + '%')
        where = '%s and status > 1 and `title` like ? ' % (where,)
    else:
        args.append(status)
        where = '%s and status = ?' % (where,)

    total = IPBlacklist.count_by(where, *args)
    page = Page(total, page_index, page_size)
    if order == 0:
        order_by = 'DESC'
    else:
        order_by = 'ASC'
    where = '%s order by updateAt %s limit ?,?' % (where, order_by)
    args.append(page.offset)
    args.append(page.limit)
    lists = IPBlacklist.find_by(where, *args)
    IP.join_by(lists, 'id', 'id')
    return lists, page.to_dict()


def _get_blacklist():
    title = ctx.request.get('title', None)
    status = ctx.request.get('status', 1)
    order = ctx.request.get('order', 0)

    lists, page = _get_blacklist_by_page(title, status, order)

    packagers = RMS.find_by('where `crm` like "%4_1_9%" and stillwork = 1')

    param = {
        'status': int(status),
        'title': title if title else ''
    }
    _format_data(lists)
    return dict(page=page, packagers=packagers, list=lists, param=param, user=ctx.request.user)


def _get_package_list():
    title = ctx.request.get('title', None)
    status = ctx.request.get('status', 2)
    order = ctx.request.get('order', 0)

    lists, page = _get_package_list_by_page(title, status, order)

    param = {
        'status': int(status),
        'title': title if title else ''
    }
    _format_data(lists)
    return dict(page=page, list=lists, param=param, user=ctx.request.user)


def _format_data(data):
    for item in data:
        item.createAt, item.updateAt = time.localtime(item.createAt), time.localtime(item.updateAt)
        item.createAt = time.strftime('%Y-%m-%d %H:%M:%S', item.createAt)
        item.updateAt = time.strftime('%Y-%m-%d %H:%M:%S', item.updateAt)

        if hasattr(item, 'blacklistUpdateAt'):
            item.blacklistUpdateAt = time.localtime(item.blacklistUpdateAt)
            item.blacklistUpdateAt = time.strftime('%Y-%m-%d %H:%M:%S', item.blacklistUpdateAt)

        if hasattr(item, 'uptime'):
            item.uptime = time.localtime(item.uptime)
            item.uptime = time.strftime('%Y-%m-%d', item.uptime)


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@view(path_join(_MODULE, 'blacklist.html'))
@get(path_join(_MODULE))
def blacklist_list():
    if ctx.request.user.crm.find('4_1_8') == -1 and ctx.request.user.crm.find('4_1_9') == -1 and ctx.request.user.crm.find('4_1_10') == -1:
        raise HttpError.seeother('/home')

    return _get_blacklist()


@api
@get(path_join(_MODULE, 'api'))
def api_blacklist_list():
    if ctx.request.user.crm.find('4_1_8') == -1 and ctx.request.user.crm.find('4_1_9') == -1 and ctx.request.user.crm.find('4_1_10') == -1:
        raise HttpError.seeother('/home')

    return _get_blacklist()


@view(path_join(_MODULE, 'vote_list.html'))
@get(path_join(_MODULE, 'voteList'))
def ip_list():
    if ctx.request.user.crm.find('4_1_8') == -1:
        raise HttpError.seeother('/home')

    return _get_votelist()


@api
@get(path_join(_MODULE, 'voteList/api'))
def api_ip_list():
    if ctx.request.user.crm.find('4_1_8') == -1:
        raise HttpError.seeother('/home')

    return _get_votelist()


@view(path_join(_MODULE, 'package_list.html'))
@get(path_join(_MODULE, 'packageList'))
def package_list():
    if ctx.request.user.crm.find('4_1_9') == -1:
        raise HttpError.seeother('/home')

    return _get_package_list()


@api
@get(path_join(_MODULE, 'packageList/api'))
def api_package_list():
    if ctx.request.user.crm.find('4_1_9') == -1:
        raise HttpError.seeother('/home')

    return _get_package_list()


@view(path_join(_MODULE, 'vote_result.html'))
@get(path_join(_MODULE, 'voteResult'))
def vote_result_list():
    if ctx.request.user.crm.find('4_1_10') == -1:
        raise HttpError.seeother('/home')

    return _get_votelist(is_admin=True)


@api
@get(path_join(_MODULE, 'voteResult/api'))
def api_vote_result_list():
    if ctx.request.user.crm.find('4_1_10') == -1:
        raise HttpError.seeother('/home')

    return _get_votelist(is_admin=True)


@api
@post(path_join(_MODULE, 'vote/api'))
def vote():
    result = int(ctx.request.get('result', None))
    ip_id = int(ctx.request.get('ipId', 0))
    reason = ctx.request.get('reason', '')

    if (result != 1 and result != 2) or ip_id <= 0 or (result == 1 and not reason):
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    if ctx.request.user.crm.find('4_1_8') == -1:
        error_code = ERROR_CODE['not_allow_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    admin_list = RMS.find_by('where `crm` like "%4_1_8%" and stillwork = 1')
    admins = admin_list[:]

    where = 'where ipId = ?'
    res = IPBlacklistVote.find_by(where, ip_id)

    pass_num, refuse_num, vote_turnout = 0, 0, 0.0

    if result == 1:
        pass_num += 1
    else:
        refuse_num += 1

    for x in res:
        if x.voterId == ctx.request.user.uid:
            error_code = ERROR_CODE['not_allow_error']
            raise APIError(error_code, ERROR_MESSAGE[error_code], {})

        if x.result == 1:
            pass_num += 1

        if x.result == 2:
            refuse_num += 1

        for admin in admin_list:
            if admin.uid == x.voterId or admin.uid == ctx.request.user.uid:
                if admin in admins:
                    admins.remove(admin)

    vote_end = 1 if len(admins) < 1 or len(admin_list) == 1 else 0
    vote_turnout = float(pass_num) / (pass_num + refuse_num)
    IPBlacklist(voteTurnout=vote_turnout, voteEnd=vote_end).update_by('where id = ?', ip_id)

    res = IPBlacklistVote(ipId=ip_id, voterId=ctx.request.user.uid, voterName=ctx.request.user.name, result=result, reason=reason, createAt=time.time(), updateAt=time.time()).insert()
    return res


@api
@get(path_join(_MODULE, 'voteDetail/api'))
def _vote_detail():
    ip_id = int(ctx.request.get('ipId', 0))

    admin_list = RMS.find_by('where `crm` like "%4_1_8%" and stillwork = 1')
    admins = admin_list[:]

    where = 'where ipId = ?'
    res = IPBlacklistVote.find_by(where, ip_id)

    for admin in admin_list:
        for x in res:
            if admin.uid == x.voterId:
                if admin in admins:
                    admins.remove(admin)

    _format_data(res)
    return dict(voteList=res, overplus=admins)


@api
@post(path_join(_MODULE, 'joinBlacklist/api'))
def _join_blacklist():
    ip_id = int(ctx.request.get('ipId', 0))
    object_id = ctx.request.get('objectId', None)
    title = ctx.request.get('title', None)
    shortcut = ctx.request.get('shortcut', None)

    if ip_id < 1:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    if ctx.request.user.crm.find('4_1_10') == -1:
        error_code = ERROR_CODE['not_allow_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    info = IPBlacklist.find_first('where id = ?', ip_id)

    if info and info.status == -1:
        raise APIError('8888', "此作品已从黑名单下线，如需上线请联系管理员！", {})

    if not shortcut:
        if not info or info.status != 0:
            error_code = ERROR_CODE['error_operation']
            raise APIError(error_code, ERROR_MESSAGE[error_code], {})

        return IPBlacklist(status=1, operatorId=ctx.request.user.uid, updateAt=time.time()).update_by('where id = ?', ip_id)
    else:
        if info:
            raise APIError('9999', "此作品已在黑名单候选流程中，无需单独添加！", {})

        if not object_id or not title:
            error_code = ERROR_CODE['param_error']
            raise APIError(error_code, ERROR_MESSAGE[error_code], {})

        return IPBlacklist(id=ip_id, status=1, operatorId=ctx.request.user.uid, updateAt=time.time(), createAt=time.time(), isShortcut=1, title=title, objectId=object_id).insert()


@api
@post(path_join(_MODULE, 'blacklistPackage/api'))
def _blacklist_package():
    ip_id = int(ctx.request.get('ipId', 0))
    packager_id = ctx.request.get('packagerId', None)
    uptime = int(ctx.request.get('uptime', 0))

    if ctx.request.user.crm.find('4_1_10') == -1:
        error_code = ERROR_CODE['not_allow_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    info = IPBlacklist.find_first('where id = ?', ip_id)

    if not info or info.status != 1:
        error_code = ERROR_CODE['error_operation']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    res = IPBlacklist(status=2, packagerId=packager_id, updateAt=time.time(), uptime=uptime).update_by('where id = ?', ip_id)
    return res
