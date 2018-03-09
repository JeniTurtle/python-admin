#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from app.models.ipsampling.ipSamplingAllot import IPSamplingAllot
from app.models.ipsampling.ipSamplingVerify import IPSamplingVerify
from app.models.user.rms import RMS
from app.models.ipverify.ipVerify import IPVerify
from app.models.ippool.ipPool import IPPool
from conf.error_code import ERROR_CODE, ERROR_MESSAGE
from lib.common import api, Page, get_page_info, check_login, get_admin_auth
from lib.core import get, ctx, view, interceptor, HttpError
from lib.error import APIError
from lib.utils import path_join

_MODULE = 'sampling'


def _get_my_ip_list_by_page(uid, allot_num, verify_result):
    page_index, page_size = get_page_info()

    if not allot_num or allot_num == 0:
        page = Page(0, page_index, page_size)
        return [], page.to_dict()

    args = [allot_num, uid]

    join = 'as a left join %s as b on a.objectId = b.objectId and a.verifyType = b.verifyType' % (IPVerify.__table__,)
    where = '%s where a.allotNum = ? and b.adminId = ?' % (join, )

    if verify_result:
        args.append(verify_result)
        where = '%s and a.verifyResult = ?' % (where,)

    total = IPSamplingVerify.count_by_field(where, 'a.id', *args)
    page = Page(total, page_index, page_size)
    where = '%s order by a.updateAt limit ?,?' % (where,)
    args.append(page.offset)
    args.append(page.limit)
    lists = IPSamplingVerify.select_by(where, args, ['a.*, b.verifyResult as ipVerifyResult'])
    IPPool.join_by(lists, 'objectId', 'objectId')

    return lists, page.to_dict()


def _format_data(data):
    for item in data:
        # 如果是ipSamplingAllot表的数据，那么createAt倒退10天
        if hasattr(item, 'owner'):
            item.createAt -= (10 * 24 * 60 * 60)

        if hasattr(item, 'rms') and item.rms.crm is not None:
            item.rms['auth_name'] = get_admin_auth(*(item.rms.crm.split(',')))

        if hasattr(item, 'allotNum') and len(str(item.allotNum)) > 0:
            item.allotNumTitle = str(item.allotNum)[0:4] + u'年' + str(item.allotNum)[4:6] + u'月'

        item.createAt, item.updateAt = time.localtime(item.createAt), time.localtime(item.updateAt)
        item.createAt = time.strftime('%Y-%m', item.createAt)
        item.updateAt = time.strftime('%Y-%m-%d %H:%M:%S', item.updateAt)

        if hasattr(item, 'publishTime'):
            item.publishTime = time.localtime(item.publishTime)
            item.publishTime = time.strftime('%Y-%m-%d', item.publishTime)


def _get_my_ip_sampling_list():
    allot_num = ctx.request.get('allotNum', 0)
    verify_result = ctx.request.get('verifyResult', None)
    uid = ctx.request.get('uid', ctx.request.user.uid)
    args = [uid]
    res = IPSamplingAllot.find_by('where owner = ? order by createAt DESC', *args)
    _format_data(res)

    if not allot_num and len(res) > 0:
        allot_num = res[0].allotNum

    lists, page = _get_my_ip_list_by_page(uid, allot_num, verify_result)
    param = {
        'allotNum': int(allot_num),
        'verifyResult': verify_result,
        'uid': uid,
    }

    if uid:
        user_info = RMS.find_first('where uid = ?', uid)
        param['name'] = user_info.name

    _format_data(lists)
    return dict(page=page, list=lists, allotList=res, param=param, user=ctx.request.user)


def _get_allot_user_by_page(allot_num):
    page_index, page_size = get_page_info()

    if not allot_num or allot_num == 0:
        page = Page(0, page_index, page_size)
        return [], page.to_dict()

    args = [allot_num]

    where = 'where `allotNum` = ?'

    total = IPSamplingAllot.count_by(where, *args)
    page = Page(total, page_index, page_size)
    where = '%s order by accuracy DESC limit ?,?' % (where,)
    args.append(page.offset)
    args.append(page.limit)
    lists = IPSamplingAllot.find_by(where, *args)
    RMS.join_by(lists, 'owner', 'uid')

    return lists, page.to_dict()


def _get_all_ip_sampling_list():
    allot_num = ctx.request.get('allotNum', 0)
    res = IPSamplingAllot.find_by('group by allotNum', )
    _format_data(res)

    if not allot_num and len(res) > 0:
        allot_num = res[0].allotNum

    lists, page = _get_allot_user_by_page(allot_num)
    param = {
        'allotNum': int(allot_num),
    }

    _format_data(lists)
    return dict(page=page, list=lists, allotList=res, param=param, user=ctx.request.user)


def _get_verify_list_by_page(verify_type='1', verify_result=None, title=None):
    page_index, page_size = get_page_info()
    join = 'as a left join %s as b on a.objectId = b.objectId' % (IPPool.__table__,)

    if title:
        args = ['%' + title + '%', ctx.request.user.uid]
        where = '%s where b.title like ? and a.verifyPerson = ?' % (join,)
    elif verify_type == '1':
        if verify_result:
            args = [verify_result, ctx.request.user.uid]
            where = '%s where a.verifyType = 1 and a.verifyResult = ? and a.verifyPerson = ?' % (join,)
        else:
            args = [verify_type, ctx.request.user.uid]
            where = '%s where a.verifyType = ? and a.verifyPerson = ?' % (join,)
    elif verify_type == '3':
        if verify_result:
            args = [verify_result, ctx.request.user.uid]
            where = '%s where (a.verifyType = 3 or a.verifyType = 4) and a.verifyResult = ? and a.verifyPerson = ?' % (join,)
        else:
            args = [ctx.request.user.uid]
            where = '%s where (a.verifyType = 3 or a.verifyType = 4) and a.verifyPerson = ?' % (join,)
    else:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    total = IPSamplingVerify.count_by_field(where, 'a.id', *args)
    page = Page(total, page_index, page_size)
    where = '%s order by updateAt limit ?,?' % (where,)
    args.append(page.offset)
    args.append(page.limit)
    lists = IPSamplingVerify.select_by(where, args, ['a.*', 'b.verifyType as ipPoolType', 'status', 'b.title', 'b.hasOutline', 'b.author', 'b.createAt as publishTime'])

    return lists, page.to_dict()


def _get_verify_list():
    verify_type = ctx.request.get('verifyType', '1')
    verify_result = ctx.request.get('verifyResult', None)
    title = ctx.request.get('title', None)
    lists, page = _get_verify_list_by_page(verify_type, verify_result, title)
    param = {
        'verifyType': verify_type,
        'verifyResult': verify_result,
        'title': title if title else '',
    }
    _format_data(lists)
    return dict(page=page, list=lists, param=param, user=ctx.request.user)


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@view(path_join(_MODULE, 'my_sampling_ip.html'))
@get(path_join(_MODULE, 'myiplist'))
def my_ip_list():
    return _get_my_ip_sampling_list()


@view(path_join(_MODULE, 'all_sampling_ip.html'))
@get(path_join(_MODULE, 'alliplist'))
def all_ip_list():
    if ctx.request.user.crm.find('4_1_5') == -1:
        raise HttpError.seeother('/sampling/myiplist')
    return _get_all_ip_sampling_list()


@view(path_join(_MODULE, 'verify_list.html'))
@get(path_join(_MODULE, 'verifylist'))
def verify_list():
    return _get_verify_list()


@api
@get(path_join(_MODULE, '/api/myiplist'))
def api_my_ip_list():
    return _get_my_ip_sampling_list()


@api
@get(path_join(_MODULE, '/api/verifylist'))
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

    # 如果缺少verify_type，或者object_id，或者verifyResult不等于1或2或3那么抛出参数错误
    if not verify_type or not object_id or (verify_result != '1' and verify_result != '2' and verify_result != '3'):
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    # 先查一次，看看这个ip是否有效，并且是否被评审过了，如果已经评审了，那么不能修改结果
    where = 'where `objectId` = ? and `verifyPerson` = ? and `verifyType` = ?'
    verify_data = IPSamplingVerify.select_by(where, [object_id, ctx.request.user.uid, verify_type], ['verifyResult'])

    if not verify_data or 'verifyResult' not in verify_data[0] or verify_data[0].verifyResult != 0:
        error_code = ERROR_CODE['not_allow_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    # 重新修改选题会作品的状态
    where = 'where objectId = ?'
    ip_info = IPPool.find_first(where, *[object_id])

    # 一抽过
    if verify_type == '1' and verify_result == '1':

        # 一审过（1，1）or 二审不过（3，2）or 二审复审不过（4，2） or 二评待审(3, 0 || 4, 0)
        if (ip_info.verifyType == 1 and ip_info.status == 1) or (ip_info.verifyType == 3 and ip_info.status == 2) or (ip_info.verifyType == 4 and ip_info.status == 2) or (ip_info.verifyType == 3 and ip_info.status == 1) or (ip_info.verifyType == 4 and ip_info.status == 1) or (ip_info.verifyType == 3 and ip_info.status == 0) or (ip_info.verifyType == 4 and ip_info.status == 0):
            pass

        # 一审不过（1，2）
        elif ip_info.verifyType == 1 and ip_info.status == 2:
            IPPool(status=1).update_by(where, *[object_id])

        else:
            raise APIError(99999991, '抽检数据存在异常！', {})

    # 一抽不过
    elif verify_type == '1' and verify_result == '2':

        # 一审过（1，1）or 二审不过（3，2）or 二审复审不过（4，2）or 二评待审(3, 0 || 4, 0)
        if (ip_info.verifyType == 1 and ip_info.status == 1) or (ip_info.verifyType == 3 and ip_info.status == 2) or (ip_info.verifyType == 4 and ip_info.status == 2):
            IPPool(verifyType=1, status=2).update_by(where, *[object_id])

        # 一审不过（1，2）
        elif (ip_info.verifyType == 1 and ip_info.status == 2) or (ip_info.verifyType == 3 and ip_info.status == 1) or (ip_info.verifyType == 4 and ip_info.status == 1) or (ip_info.verifyType == 3 and ip_info.status == 0) or (ip_info.verifyType == 4 and ip_info.status == 0):
            pass

        else:
            raise APIError(99999992, '抽检数据存在异常！', {})

    # 二抽过
    elif verify_type == '3' and verify_result == '1':

        # 一审不过（1，2）or 二审不过（3，2）
        if (ip_info.verifyType == 1 and ip_info.status == 2) or (ip_info.verifyType == 3 and ip_info.status == 2) or (ip_info.verifyType == 4 and ip_info.status == 2):
            ip_verify_type = 4 if ip_info.thirdOldStatus > 0 else 3
            IPPool(verifyType=ip_verify_type, status=1).update_by(where, *[object_id])

        # 二审过（3，1）
        elif (ip_info.verifyType == 3 and ip_info.status == 1) or (ip_info.verifyType == 4 and ip_info.status == 1):
            pass

        else:
            raise APIError(99999993, '抽检数据存在异常！', {})

    # 二抽不过
    elif verify_type == '3' and verify_result == '2':

        # 一审不过（1，2）or 二审不过（3，2）
        if (ip_info.verifyType == 1 and ip_info.status == 2) or (ip_info.verifyType == 3 and ip_info.status == 2) or (ip_info.verifyType == 4 and ip_info.status == 2):
            pass

        # 二审过（2，1）
        elif (ip_info.verifyType == 3 and ip_info.status == 1) or (ip_info.verifyType == 4 and ip_info.status == 1):
            IPPool(status=2).update_by(where, *[object_id])

        else:
            raise APIError(99999994, '抽检数据存在异常！', {})

    # 复审二抽过
    elif verify_type == '4' and verify_result == '1':

        # 一审不过（1，2）or 二审复审不过（4，2）
        if (ip_info.verifyType == 1 and ip_info.status == 2) or (ip_info.verifyType == 4 and ip_info.status == 2):
            IPPool(verifyType=4, status=1).update_by(where, *[object_id])

        # 二审复审过（4，1）
        elif ip_info.verifyType == 4 and ip_info.status == 1:
            pass

        else:
            raise APIError(99999995, '抽检数据存在异常！', {})

    # 复审二抽不过
    elif verify_type == '4' and verify_result == '2':

        # 一审不过（1，2）or 二审复审不过（4，2）
        if (ip_info.verifyType == 1 and ip_info.status == 2) or (ip_info.verifyType == 4 and ip_info.status == 2):
            pass

        # 二审复审过（3，1）
        elif ip_info.verifyType == 4 and ip_info.status == 1:
            IPPool(status=2).update_by(where, *[object_id])

        else:
            raise APIError(99999996, '抽检数据存在异常！', {})

    where = 'where `objectId` = ? and `verifyPerson` = ? and `verifyType` = ?'
    ip_verify = IPSamplingVerify(verifyResult=verify_result, updateAt=time.time())
    res = ip_verify.update_by(where, object_id, ctx.request.user.uid, verify_type)

    # 判断下返回的结果是不是存在问题
    if not hasattr(res, 'verifyResult') or res.verifyResult != verify_result:
        IPPool(verifyType=ip_info.verifyType, status=ip_info.status).update_by(where, *[object_id])
        error_code = ERROR_CODE['update_sql_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    return res




