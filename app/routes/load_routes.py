#!/usr/bin/env python
# -*- coding: utf-8 -*-

import app.routes.test.test_route as test
import app.routes.home.home_route as home
import app.routes.user.user_route as user
import app.routes.user.login_route as login
import app.routes.ippool.ipPool_route as ip_pool
import app.routes.ipverify.verify_route as ip_verify
import app.routes.ipsampling.sampling_route as ip_sampling
import app.routes.newwriter.newwriter_route as newwriter
import app.routes.blacklist.ipBlacklist_route as blacklist
import app.routes.dci.dci_route as dci
import app.routes.whitelist.whitelist_route as whitelist


def load(wsgi):
    # 测试模块
    wsgi.add_interceptor(test.user_interceptor)
    wsgi.add_interceptor(test.manage_interceptor)
    wsgi.add_module(test)

    # 登录管理模块
    wsgi.add_module(login)

    # 首页
    wsgi.add_interceptor(home.check_login_interceptor)
    wsgi.add_module(home)

    # 用户管理模块
    wsgi.add_interceptor(user.check_login_interceptor)
    wsgi.add_module(user)

    # 作品列表模块
    wsgi.add_interceptor(ip_pool.check_login_interceptor)
    wsgi.add_module(ip_pool)

    # 选题会任务模块
    wsgi.add_interceptor(ip_verify.check_login_interceptor)
    wsgi.add_module(ip_verify)

    # 抽检模块
    wsgi.add_interceptor(ip_sampling.check_login_interceptor)
    wsgi.add_module(ip_sampling)

    # 新编剧模块
    wsgi.add_interceptor(newwriter.check_login_interceptor)
    wsgi.add_interceptor(newwriter.check_auth_interceptor)
    wsgi.add_module(newwriter)

    # 黑名单模块
    wsgi.add_interceptor(blacklist.check_login_interceptor)
    wsgi.add_module(blacklist)

    # 版保模块
    wsgi.add_interceptor(dci.check_login_interceptor)
    wsgi.add_module(dci)

    # 白名单模块
    wsgi.add_interceptor(whitelist.check_login_interceptor)
    wsgi.add_module(whitelist)
