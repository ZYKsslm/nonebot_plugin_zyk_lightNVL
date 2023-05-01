# -*- coding: utf-8 -*-
from nonebot import get_driver
from browser_cookie3 import load
from selenium import webdriver
from os import path


class NoCookies(Exception):
    def __str__(self):
        return "未获取到cookies，请在浏览器中访问https://w.linovelib.com/search.html并重启bot！"

# 获取cookies
def reset_cookies():
    cookies = load(domain_name="w.linovelib.com")
    if not cookies:
        raise NoCookies
    return cookies

cookies = reset_cookies()


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

# 获取搜索结果发送失败时重新发送的条数
try:
    show_all = get_driver().config.light_nvl_show_all
except AttributeError:
    show_all = False


driver = webdriver.PhantomJS(executable_path=path.join(path.abspath(path.dirname(__file__)), "phantomjs/bin/phantomjs.exe"))