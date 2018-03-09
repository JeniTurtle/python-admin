#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import math
from lib.core import get, ctx, view, interceptor
from lib.common import api, Page, get_page_info, check_login, get_admin_auth
from lib.utils import path_join
from lib.error import APIError
from conf.error_code import ERROR_CODE, ERROR_MESSAGE
from app.models.user.ipPoolAdmin import IpPoolAdmin
from app.models.user.rms import RMS
from app.models.user.user import User
from app.models.ipverify.ipVerify import IPVerify

_MODULE = 'user'


def _get_users_by_page(crm=None, mobile=None):
    page_index, page_size = get_page_info()

    where, args = None, []

    if crm and mobile:
        args = ['%' + crm + '%', mobile]
        where = 'where `crm` like ? and `mobile` = ?'
    elif crm and not mobile:
        args = ['%' + crm + '%']
        where = 'where `crm` like ?'
    elif not crm and mobile:
        args = [mobile]
        where = 'where `mobile` = ?'
    else:
        where = 'where length(crm) > 0'

    if not where:
        total = RMS.count_all()
    else:
        total = RMS.count_by(where, *args)

    page = Page(total, page_index, page_size)
    args.append(page.offset)
    args.append(page.limit)

    where = '%s order by id desc limit ?,?' % (where,)
    users = RMS.find_by(where, *args)

    IpPoolAdmin.join_by(users, 'uid', 'uid')

    _format_data(users)
    return users, page.to_dict()


def _format_data(data):
    for item in data:
        verify_count, verify_time = 0, 6
        where = 'where adminId = ? and ipAllotId != -1 and verifyType = 1 and verifyResult > 0 group by days'
        if item.crm.find('4_1_3') > -1:
            verify_time = 10
            where = 'where adminId = ? and ipAllotId != -1 and verifyResult > 0 and (verifyType = 3 or verifyType = 4) group by days'

        verify_info = IPVerify.select_by(where, [item.uid], ['updateAt', 'FROM_UNIXTIME(updateAt,"%Y%m%d") as days', 'count(id) as count'])
        first_days, loop_num = 0, 0;
        for info in verify_info:
            if loop_num == 0:
                first_days = info.updateAt
            loop_num += 1
            verify_count += info.count

        date = ((time.time() - first_days) / 60 / 60 / 24) * 5 / 7
        date = math.ceil(date)
        item.everyday_time = 0 if len(verify_info) < 1 else (float(verify_count) * verify_time / date / 60)
        item.everyday_time = round(item.everyday_time, 2)

        item.counts = verify_count
        item.days = date
        item.firstDay = first_days

        if hasattr(item, 'crm'):
            item['auth_name'] = get_admin_auth(*(item.crm.split(',')))

        if not item.ipPoolAdmin:
            continue
        item.ipPoolAdmin.createAt, item.ipPoolAdmin.updateAt = time.localtime(item.ipPoolAdmin.createAt), time.localtime(item.ipPoolAdmin.updateAt)
        item.ipPoolAdmin.createAt = time.strftime('%Y-%m-%d %H:%M:%S', item.ipPoolAdmin.createAt)
        item.ipPoolAdmin.updateAt = time.strftime('%Y-%m-%d %H:%M:%S', item.ipPoolAdmin.updateAt)


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@view(path_join(_MODULE, 'user_list.html'))
@get(path_join(_MODULE))
def user_list():
    crm = ctx.request.get('crm', None)
    mobile = ctx.request.get('mobile', None)
    users, page = _get_users_by_page(crm, mobile)
    return dict(page=page, list=users, user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/list'))
def _api_user_list():
    crm = ctx.request.get('crm', None)
    mobile = ctx.request.get('mobile', None)
    users, page = _get_users_by_page(crm, mobile)
    return dict(page=page, list=users, user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/searchUserInfo'))
def _search_user_info():
    key = ctx.request.get('key', None)
    if not key:
        error_code = ERROR_CODE['param_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})

    keys, i = [], 0

    while i < 7:
        keys.append("%" + key + "%")
        i += 1

    where = 'where `username` like ? or `desc` like ? or `company` like ? or `companyShortName` like ? or `person_name` like ? or `person_nickname` like ? or `person_desc` like ?'
    data = User.find_by(where, *keys)
    return dict(user=data)
