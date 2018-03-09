#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re, hashlib, logging, time

import lib.markdown as markdown
from conf.config import configs
from lib.core import get, post, ctx, view, interceptor, HttpError
from lib.error import APIError, APIValueError, APIResourceNotFoundError, APIPermissionError
from lib.common import api, Page, check_admin
from lib.utils import next_id, path_join

from app.models.test.blogs import Blogs
from app.models.test.users import Users
from app.models.test.comments import Comments

_MODULE = 'test'

COOKIE_NAME = 'awesession'
COOKIE_KEY = configs.session.secret


def make_signed_cookie(id, password, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, password, expires, COOKIE_KEY)).hexdigest()]
    return '-'.join(L)


def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = Users.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None


def _get_page_index():
    page_index = 1
    try:
        page_index = int(ctx.request.get('page', '1'))
    except ValueError:
        pass
    return page_index


def _get_blogs_by_page():
    total = Blogs.count_all()
    page = Page(total, _get_page_index())
    blogs = Blogs.find_by('order by created_at desc limit ?,?', page.offset, page.limit)
    return blogs, page.to_dict()


@interceptor(path_join(_MODULE, '/'))
def user_interceptor(next):
    logging.info('try to bind user from session cookie...')
    user = None
    cookie = ctx.request.cookies.get(COOKIE_NAME)
    if cookie:
        logging.info('parse session cookie...')
        user = parse_signed_cookie(cookie)
        if user:
            logging.info('bind user <%s> to session...' % user.email)
    ctx.request.user = user
    return next()


@interceptor(path_join(_MODULE, '/manage'))
def manage_interceptor(next):
    user = ctx.request.user
    if user and user.admin:
        return next()
    raise HttpError.seeother(path_join(_MODULE, '/signin'))


@view(path_join(_MODULE, 'blogs.html'))
@get(path_join(_MODULE, '/'))
def index():
    blogs, page = _get_blogs_by_page()
    return dict(page=page, blogs=blogs, user=ctx.request.user)


@view(path_join(_MODULE, 'blog.html'))
@get(path_join(_MODULE, '/blog/:blog_id'))
def blog(blog_id):
    blog = Blogs.get(blog_id)
    if blog is None:
        raise HttpError.notfound()
    blog.html_content = markdown.markdown(blog.content)
    comments = Comments.find_by('where blog_id=? order by created_at desc limit 1000', blog_id)
    return dict(blog=blog, comments=comments, user=ctx.request.user)


@view(path_join(_MODULE, 'signin.html'))
@get(path_join(_MODULE, '/signin'))
def signin():
    return dict()


@get(path_join(_MODULE, '/signout'))
def signout():
    ctx.response.delete_cookie(COOKIE_NAME)
    raise HttpError.seeother(path_join(_MODULE, '/'))


@api
@post(path_join(_MODULE, '/api/authenticate'))
def authenticate():
    i = ctx.request.input(remember='')
    email = i.email.strip().lower()
    password = i.password
    remember = i.remember
    user = Users.find_first('where email=?', email)
    if user is None:
        raise APIError('auth:failed', 'email', 'Invalid email.')
    elif user.password != password:
        raise APIError('auth:failed', 'password', 'Invalid password.')
    # make session cookie:
    max_age = 604800 if remember=='true' else None
    cookie = make_signed_cookie(user.id, user.password, max_age)
    ctx.response.set_cookie(COOKIE_NAME, cookie, max_age=max_age)
    user.password = '******'
    return user

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')


@api
@post(path_join(_MODULE, '/api/users'))
def register_user():
    i = ctx.request.input(name='', email='', password='')
    name = i.name.strip()
    email = i.email.strip().lower()
    password = i.password
    if not name:
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not password or not _RE_MD5.match(password):
        raise APIValueError('password')
    user = Users.find_first('where email=?', email)
    if user:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    user = Users(id=next_id(), name=name, email=email, password=password, image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email).hexdigest())
    user.insert()
    # make session cookie:
    cookie = make_signed_cookie(user.id, user.password, None)
    ctx.response.set_cookie(COOKIE_NAME, cookie)
    return user


@view(path_join(_MODULE, 'register.html'))
@get(path_join(_MODULE, '/register'))
def register():
    return dict()


@get(path_join(_MODULE, '/manage'))
def manage_index():
    raise HttpError.seeother(path_join(_MODULE, '/manage/comments'))


@view(path_join(_MODULE, 'manage_comment_list.html'))
@get(path_join(_MODULE, '/manage/comments'))
def manage_comments():
    return dict(page_index=_get_page_index(), user=ctx.request.user)


@view(path_join(_MODULE, 'manage_blog_list.html'))
@get(path_join(_MODULE, '/manage/blogs'))
def manage_blogs():
    return dict(page_index=_get_page_index(), user=ctx.request.user)


@view(path_join(_MODULE, 'manage_blog_edit.html'))
@get(path_join(_MODULE, '/manage/blogs/create'))
def manage_blogs_create():
    return dict(id=None, action=path_join(_MODULE, '/api/blogs'), redirect=path_join(_MODULE, '/manage/blogs'), user=ctx.request.user)


@view(path_join(_MODULE, 'manage_blog_edit.html'))
@get(path_join(_MODULE, '/manage/blogs/edit/:blog_id'))
def manage_blogs_edit(blog_id):
    blog = Blogs.get(blog_id)
    if blog is None:
        raise HttpError.notfound()
    return dict(id=blog.id, name=blog.name, summary=blog.summary, content=blog.content, action=path_join(_MODULE, '/api/blogs/%s' % blog_id), redirect=path_join(_MODULE, '/manage/blogs'), user=ctx.request.user)


@view(path_join(_MODULE, 'manage_user_list.html'))
@get(path_join(_MODULE, '/manage/users'))
def manage_users():
    return dict(page_index=_get_page_index(), user=ctx.request.user)


@api
@get(path_join(_MODULE, '/api/blogs'))
def api_get_blogs():
    format = ctx.request.get('format', '')
    blogs, page = _get_blogs_by_page()
    if format=='html':
        for blog in blogs:
            blog.content = markdown.markdown(blog.content)
    return dict(blogs=blogs, page=page)


@api
@get(path_join(_MODULE, '/api/blogs/:blog_id'))
def api_get_blog(blog_id):
    blog = Blogs.get(blog_id)
    if blog:
        return blog
    raise APIResourceNotFoundError('Blog')


@api
@post(path_join(_MODULE, '/api/blogs'))
def api_create_blog():
    check_admin()
    i = ctx.request.input(name='', summary='', content='')
    name = i.name.strip()
    summary = i.summary.strip()
    content = i.content.strip()
    if not name:
        raise APIValueError('name', 'name cannot be empty.')
    if not summary:
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')
    user = ctx.request.user
    blog = Blogs(user_id=user.id, user_name=user.name, name=name, summary=summary, content=content)
    blog.insert()
    return blog


@api
@post(path_join(_MODULE, '/api/blogs/:blog_id'))
def api_update_blog(blog_id):
    check_admin()
    i = ctx.request.input(name='', summary='', content='')
    name = i.name.strip()
    summary = i.summary.strip()
    content = i.content.strip()
    if not name:
        raise APIValueError('name', 'name cannot be empty.')
    if not summary:
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blogs.get(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    blog.name = name
    blog.summary = summary
    blog.content = content
    blog.update()
    return blog


@api
@post(path_join(_MODULE, '/api/blogs/:blog_id/delete'))
def api_delete_blog(blog_id):
    check_admin()
    blog = Blogs.get(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    blog.delete()
    return dict(id=blog_id)


@api
@post(path_join(_MODULE, '/api/blogs/:blog_id/comments'))
def api_create_blog_comment(blog_id):
    user = ctx.request.user
    if user is None:
        raise APIPermissionError('Need signin.')
    blog = Blogs.get(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    content = ctx.request.input(content='').content.strip()
    if not content:
        raise APIValueError('content')
    c = Comments(blog_id=blog_id, user_id=user.id, user_name=user.name, user_image=user.image, content=content)
    c.insert()
    return dict(comment=c)


@api
@post(path_join(_MODULE, '/api/comments/:comment_id/delete'))
def api_delete_comment(comment_id):
    check_admin()
    comment = Comments.get(comment_id)
    if comment is None:
        raise APIResourceNotFoundError('Comment')
    comment.delete()
    return dict(id=comment_id)


@api
@get(path_join(_MODULE, '/api/comments'))
def api_get_comments():
    total = Comments.count_all()
    page = Page(total, _get_page_index())
    comments = Comments.find_by('order by created_at desc limit ?,?', page.offset, page.limit)
    return dict(comments=comments, page=page.to_dict())


@api
@get(path_join(_MODULE, '/api/users'))
def api_get_users():
    total = Users.count_all()
    page = Page(total, _get_page_index())
    users = Users.find_by('order by created_at desc limit ?,?', page.offset, page.limit)
    for u in users:
        u.password = '******'
    return dict(users=users, page=page.to_dict())