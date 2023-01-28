# -*- coding: utf-8 -*-
from nonebot import get_driver


# 获取用户名
try:
    username = get_driver().config.light_nvl_username
except AttributeError:
    username = None

# 获取密码
try:
    password = get_driver().config.light_nvl_password
except AttributeError:
    password = None

# 获取搜索结果发送失败时重新发送的条数
try:
    retry_num = get_driver().config.light_nvl_retry_num
except AttributeError:
    retry_num = 50


# 获取cookie
try:
    cookie = get_driver().config.light_nvl_cookie
except AttributeError:
    cookie = None