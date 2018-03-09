#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
error file
"""


class DBError(Exception):
    pass


class MultiColumnsError(DBError):
    pass


class APIError(StandardError):
    """
    the base APIError which contains error(required), data(optional) and message(optional).
    存储所有API 异常对象的数据
    """
    def __init__(self, error, message='', data=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class APIValueError(APIError):
    """
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    输入不合法 异常对象
    """
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    """
    Indicate the resource was not found. The data specifies the resource name.
    资源未找到 异常对象
    """
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)


class APIPermissionError(APIError):
    """
    Indicate the api has no permission.
    权限 异常对象
    """
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)
