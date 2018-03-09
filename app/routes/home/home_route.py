#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.models.ippool.ipPool import IPPool
from app.models.ipverify.ipVerify import IPVerify
from app.models.ipsampling.ipSamplingVerify import IPSamplingVerify
from lib.core import get, ctx, view, interceptor
from lib.common import check_login, api
from lib.utils import path_join

_MODULE = 'home'


def _get_verify_count(uid=None):
    data = {}
    uid = uid or ctx.request.user.uid
    args = [uid]
    join = 'as a left join %s as b on a.objectId = b.objectId where b.discard = 0' % (IPPool.__table__,)
    where = "%s and a.adminId = ? and a.verifyResult = 0" % (join,)
    data['pendingCount'] = IPVerify.count_by_field(where, 'a.id', *args)
    where = "%s and a.adminId = ? and (a.verifyResult = 1 or a.verifyResult = 2)" % (join,)
    data['verifiedCount'] = IPVerify.count_by_field(where, 'a.id', *args)
    where = "%s and a.verifyPerson = ? and a.verifyResult = 0" % (join,)
    data['samplingPendingCount'] = IPSamplingVerify.count_by_field(where, 'a.id', *args)
    where = "%s and a.verifyPerson = ? and (a.verifyResult = 1 or a.verifyResult = 2)" % (join,)
    data['samplingVerifiedCount'] = IPSamplingVerify.count_by_field(where, 'a.id', *args)
    return data


@interceptor(path_join(_MODULE))
def check_login_interceptor(next):
    return check_login(next)


@view(path_join(_MODULE, 'home.html'))
@get(path_join(_MODULE))
def home():
    data = _get_verify_count()
    return dict(data=data, user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/verifycount'))
def verify_count():
    uid = ctx.request.get('uid', None)
    data = _get_verify_count(uid)
    return dict(data=data)

