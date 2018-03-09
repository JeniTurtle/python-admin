#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import time
from conf.env import ENV
from conf.cookie_list import LOGIN_COOKIE_NAME
from conf.error_code import ERROR_CODE, ERROR_MESSAGE
from lib.core import get, post, ctx, view, HttpError, interceptor
from lib.error import APIError
from lib.common import api, make_signed_cookie, parse_signed_cookie
from lib.utils import path_join
from app.models.user.rms import RMS
from app.models.user.ipPoolAdmin import IpPoolAdmin

_MODULE = 'login'

_LOGIN_URL = {
    'production': 'http://y.yunlaiwu.com/sns/luser/passlogin?username=%s&password=%s',
    'development': 'http://testapi.yunlaiwu.com:8099/sns/luser/passlogin?username=%s&password=%s'
}[ENV]


def _login(phone, password):
    url = _LOGIN_URL % (phone, password)
    res_data = urllib2.urlopen(url)
    res = res_data.read()
    res_data.close()
    return json.loads(res)


# 这里木有调用，允许用户在登录的情况下访问登录页面
@interceptor(path_join(_MODULE))
def user_interceptor(next):
    cookie = ctx.request.cookies.get(LOGIN_COOKIE_NAME)
    ctx.request.user = None
    if cookie:
        user = parse_signed_cookie(cookie)
        if user and user.id:
            raise HttpError.seeother('/home')
    return next()


@view(path_join(_MODULE, 'login.html'))
@get(path_join(_MODULE))
def login():
    return dict()


@api
@get(path_join(_MODULE, '/api'))
@post(path_join(_MODULE, '/api'))
def authenticate():
    i = ctx.request.input(remember='')
    phone = i.phone.strip()
    password = i.password
    user = RMS.find_first('where mobile = ? and crm is not null and stillwork = 1', phone)
    if user is None:
        error_code = ERROR_CODE['user_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code])

    login_info = _login(phone, password)

    if login_info['errno'] != 0 or not login_info['data'] or not login_info['data']['sessionToken']:
        error_code = ERROR_CODE['login_error']
        raise APIError(error_code, ERROR_MESSAGE[error_code], {})
    else:
        # 如果登录成功，查看ipPoolAdmin表，如果木有该用户，那么增加这个用户，否则更新下登录时间
        count = IpPoolAdmin.count_by('where uid = ?', user.uid)

        if count < 1:
            IpPoolAdmin(uid=user.uid).insert()
        else:
            IpPoolAdmin(createAt=time.time()).update_by('where `uid` = ?', user.uid)

        max_age = 86400
        cookie = make_signed_cookie(str(user.id), user.mobile, max_age)
        ctx.response.set_cookie(LOGIN_COOKIE_NAME, cookie, max_age=max_age)
        ctx.response.set_cookie('leancloud-token', login_info['data']['sessionToken'], max_age=max_age)
        return user
