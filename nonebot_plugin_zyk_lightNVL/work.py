from httpx import AsyncClient
import re
from os import path
from lxml import html
from nonebot_plugin_htmlrender import html_to_pic
from fake_useragent import UserAgent
from time import time


async def get_checkcode():
    checkcode_api = "https://w.linovelib.com/checkcode.php"
    headers = {
        "origin": "https://w.linovelib.com",
        "referer": "https://w.linovelib.com/login.php",
        "User-Agent": UserAgent().random
    }
    param = {
        "rand": int(time())
    }

    client = AsyncClient(headers=headers, timeout=None)
    r = await client.get(checkcode_api, params=param)

    return client, r.content


async def login(client: AsyncClient, username, password, checkcode):
    login_api = "https://w.linovelib.com/login.php?do=submit&jumpurl=https%3A%2F%2Fw.linovelib.com%2F"
    data = {
        "username": username,
        "password": password,
        "checkcode": checkcode,
        "act": "login",
        "usecookie": "86400",
        "submit": ""
    }
    resp = await client.post(url=login_api, data=data)

    if resp.status_code != 302:
        info = re.findall(r'<div class="aui-ver-form">(.*?)<br>', resp.text, re.S)[0].replace("\n", "")
        return False, info
    else:
        cookie_path = path.join(path.abspath(path.dirname(__file__)), "cookie.txt")
        with open(file=cookie_path, mode="w", encoding="utf-8") as f:
            f.write(resp.headers["set-cookie"])
        return True, client


async def search(client: AsyncClient, name, retry_num):

    # 检索书名
    url = "https://w.linovelib.com/S8/"
    data = {
        "searchkey": name,
        "searchtype": "all"
    }

    resp = await client.get(url=url, params=data)
    info = resp.text

    # 获取书名信息列表
    book_list = re.findall(r'class="book-cover" alt="(.*?)">', info)

    # 没有重定向且有多个结果
    if len(book_list) > 1:
        href_list = [
            "https://w.linovelib.com" + href
            for href in re.findall(r'<a href="(.*?)" class="book-layout"', info)
        ]
        next_page = re.findall(r'</span><a href="(.*?)" class="next">', info)[0]
        if next_page == "#":
            return book_list, href_list

        # 不止一页
        if retry_num < 30:
            page = 1
        else:
            page = retry_num // 30
            if retry_num % 30 != 0:
                page += 1

        for _ in range(page-1):
            if next_page == "#":
                break
            next_page = "https://w.linovelib.com" + next_page
            info = (await client.get(url=next_page)).text
            # 获取书名信息列表
            books = re.findall(r'class="book-cover" alt="(.*?)">', info)
            hrefs = [
                "https://w.linovelib.com" + href
                for href in re.findall(r'<a href="(.*?)" class="book-layout"', info)
            ]
            book_list += books
            href_list += hrefs

            next_page = re.findall(r'</span><a href="(.*?)" class="next">', info)[0]

        return book_list, href_list

    # 重定向（直接跳转到书页）
    elif "/novel/" in str(resp.url):
        pattern = re.compile(r'<meta property="og:title" content="(.*?)" />')
        book_name = [re.findall(pattern, info)[0]]

        return book_name, [str(resp.url)]

    else:
        return False


async def get_content(client: AsyncClient, book_url):
    book_info = (await client.get(url=book_url)).text

    content_pattern = re.compile(r'(<div class="module module-merge">.*?)<div class="module">', re.S)
    index_pattern = re.compile(r'<li class="btn-group-cell"><a href="(.*?)"')
    info_pattern = re.compile(r'<div id="bookDetailWrapper" class="module module-merge book-detail-x">.*?</span>\n</p>\n\n</div>\n</div>', re.S)

    info = re.findall(info_pattern, book_info)[0]
    content = re.findall(content_pattern, book_info)[0]
    index_url = "https://w.linovelib.com" + re.findall(index_pattern, book_info)[0]

    try:
        book_id = re.findall(r'https://w.linovelib.com/novel/(\d+).html', book_url)[0]
    except IndexError:
        book_id = re.findall(r'acode=i_(\d+)', book_url)[0]

    html_path = path.join(path.abspath(path.dirname(__file__)), "template.html")
    with open(html_path, "r", encoding="utf-8") as h:
        template = h.read()
    content = template.format(content=content, info=info)
    pic = await html_to_pic(html=content)

    return pic, index_url, book_id


async def get_bookcase(client: AsyncClient):
    resp = await client.get(url="https://w.linovelib.com/bookcase.php")

    if "login" in str(resp.url):
        return False
    case_info = resp.text
    book_pattern = re.compile(r'<h4 class="book-title">(.*?)</h4>')
    url_pattern = re.compile(r'<a href="(.*?)" class="mybook-to-detail">')
    books = re.findall(book_pattern, case_info)
    urls = re.findall(url_pattern, case_info)

    return books, urls
