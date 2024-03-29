from httpx import AsyncClient
import re
from fake_useragent import UserAgent
from time import time
from asyncio import sleep
import atexit
from .config import *



def html_parse(episodes=None, index_dict=None, chapter=None):

    html_text = f'''<!DOCTYPE html>
    <html lang="zh-Hans">
    <head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://w.linovelib.com/themes/zhmb/css/info.css?v0509c1">
    </head>
    <body>
    <div id="content">
    <ol id="volumes" class="chapter-ol chapter-ol-catalog">
    '''
    if index_dict is not None:
        for chapter, episodes in index_dict.items():
            html_text += f'''
            <li class="chapter-bar chapter-li">{chapter}</li>
            '''
            for episode in episodes:
                html_text += f'''<li class="chapter-li jsChapter"><a class="chapter-li-a "><span class="chapter-index ">{episode}</span></a></li>
                '''
    else:
        html_text += f'''
        <li class="chapter-bar chapter-li">{chapter}</li>
        '''
        for episode in episodes:
                html_text += f'''<li class="chapter-li jsChapter"><a class="chapter-li-a "><span class="chapter-index ">{episode}</span></a></li>
                '''

    html_text += '''
    </ol>
    </div>
    </body>
    </html>
    '''

    html_path = path.join(path.abspath(path.dirname(__file__)), "index.html")
    with open(html_path, "w+", encoding="utf-8") as f:
        f.write(html_text)

    return html_path


async def index_parse(index_info):

    chapter_info = re.findall(r'([\u4e00-\u9fa5\s\dA-Za-z（）]+)(</li>.*?<li class="chapter-li jsChapter"><a.*?)(<li class="chapter-bar chapter-li">|</ol>.*?</div>)', index_info, re.S)
    
    index_dict = {}
    for res in chapter_info:
        chapter, episode_info = res[0], res[1]
        episodes = re.findall(r'<span class="chapter-index ">(.*?)</span></a>', episode_info)
        index_dict.update(
            {
                chapter: episodes
            }
        )
    
    return index_dict


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

    client = AsyncClient(headers=headers, timeout=None, cookies=cookies)
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

    # 登录成功将会重定向
    if resp.status_code != 302:
        info = re.findall(r'<div class="aui-ver-form">(.*?)<br>', resp.text, re.S)[0].replace("\n", "")
        return False, info

    client.follow_redirects = True
        
    return True, client


async def search(client: AsyncClient, name, retry_num):

    # 检索书名
    url = "https://w.linovelib.com/search.html"
    data = {
        "searchkey": name,
    }
    headers = {
        "referer": "https://w.linovelib.com/search.html",
        "oringin": "https://w.linovelib.com",
        "method": "POST",
        "User-Agent": UserAgent().random
    }

    resp = await client.post(url=url, data=data, headers=headers)
    info = resp.text

    # 重定向（直接跳转到书页）
    if "/novel/" in str(resp.url):
        return "book_page", info, str(resp.url)

    # 没有重定向且有多个结果
    elif '<meta name="robots" content="noindex,nofollow">' not in info:
        book_list, href_list, next_page = search_parse(info)
        
        if (next_page is None) or (show_all is False):
            return book_list, href_list

        # 不止一页，根据retry_num选择需要多少页
        if retry_num < 30:
            page = 1
        else:
            page = retry_num // 30
            if retry_num % 30 != 0:
                page += 1

        for _ in range(page - 1):
            if next_page == "#":
                break
            await sleep(3)
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

    # 无结果
    else:
        return False


def search_parse(res):
    # 获取书名信息列表
    book_list = re.findall(r'alt="(.*?)"', res, re.S)
    href_list = [
        "https://w.linovelib.com" + href
        for href in re.findall(r'<li class="book-li"><a href="(.*?)" class="book-layout">', res)
    ]
    next_page = re.findall(r'</span><a href="(.*?)" class="next">', res)[0]
    if next_page == "#":
        return book_list, href_list, None
    else:
        return book_list, href_list, "https://w.linovelib.com" + next_page


def browser_size_reset():
    # 使用execute_script方法获取网页的宽度和高度
    width = driver.execute_script("return document.body.clientWidth")
    height = driver.execute_script("return document.body.clientHeight")

    # 使用set_window_size方法调整浏览器窗口的大小
    driver.set_window_size(width,height)


# 防止程序强制退出，关闭浏览器
@atexit.register
def quit():
    driver.quit()


async def get_content(book_info):

    content_pattern = re.compile(r'(<!DOCTYPE html>.*)<style>.page-fans', re.S)
 
    content = re.findall(content_pattern, book_info)[0]

    html_path = path.join(path.abspath(path.dirname(__file__)), "template.html")
    with open(html_path, "w+", encoding="utf-8") as h:
        h.write(content)

    driver.get(f'file:///{html_path}')
    driver.implicitly_wait(2)
    
    if browser != "phantomjs":
        browser_size_reset()

    pic = driver.get_screenshot_as_png()

    return pic


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
