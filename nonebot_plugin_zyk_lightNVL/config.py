# -*- coding: utf-8 -*-
from nonebot import get_driver
from browser_cookie3 import load
from selenium import webdriver
from os import path


# 获取浏览器缓存cookies
cookies = load(domain_name="w.linovelib.com")

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

# 获取浏览器
try:
    browser = get_driver().config.light_nvl_browser
except AttributeError:
    browser = "phantomjs"
if browser != "Chrome" or browser != "chrome":
    browser = "phantomjs"

# 获取chromedriver_path的路径
try:
    chromedriver_path = get_driver().config.light_nvl_chromedriver_path
except AttributeError:
    chromedriver_path = None


if browser == "Chrome" or browser == "chrome":
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # 创建一个webdriver.Chrome对象，并传入chrome_options和executable_path参数
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver_path)
    
else:
    driver = webdriver.PhantomJS(executable_path=path.join(path.abspath(path.dirname(__file__)), "phantomjs/bin/phantomjs.exe"))