#!/usr/bin/env python
# -*- coding: utf-8 -*-

ERROR_CODE = {
    # 登录、注册错误码
    'user_error': 101,
    'password_error': 102,
    'login_error': 103,

    # 请求参数错误码
    'param_error': 201,

    # 权限限制
    'not_allow_error': 202,

    # 操作不允许
    'error_operation': 203,

    # 操作数据库错误
    'update_sql_error': 301,
    'insert_sql_error': 302,

    # 数据异常
    'data_exception_error': 401,
}

ERROR_MESSAGE = {
    101: 'Invalid user',
    102: 'Password error',
    103: 'Login fail',

    201: 'Wrong parameter',
    202: 'Operation not allowed',
    203: 'Error operation',

    301: 'Failed to update database',
    302: 'Insert database failed',

    401: 'Data exception'
}
