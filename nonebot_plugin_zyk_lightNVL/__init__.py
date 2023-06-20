# -*- coding: utf-8 -*-
from nonebot.adapters.onebot.v11 import GROUP, PRIVATE_FRIEND, Message, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.exception import ActionFailed
from nonebot.params import Arg, T_State, CommandArg

from colorama import init, Fore
from .work import *

__version__ = "0.3.1"

login_matcher = on_command(cmd="nvl_login", priority=5, permission=SUPERUSER)
id_matcher = on_command(cmd="nvl_id", priority=5, permission=GROUP | PRIVATE_FRIEND, block=True)
bookcase_matcher = on_command(cmd="nvl_bookcase", priority=5, permission=GROUP | PRIVATE_FRIEND, block=True)
book_matcher = on_command(cmd="nvl", priority=5, permission=GROUP | PRIVATE_FRIEND, block=True)
cookies_matcher = on_command(cmd="nvl_cookies", priority=5, permission=SUPERUSER, block=True)

# 字体样式初始化（自动重设字体样式）
init(autoreset=True)

# 初始请求状态
client = AsyncClient(
    headers={
        "origin": "https://w.linovelib.com",
        "User-Agent": UserAgent().random
    },
    timeout=None,
    follow_redirects=True,
    cookies=cookies
)

logger.success(Fore.LIGHTGREEN_EX + f"成功导入本插件，插件版本为{__version__}")


# 登录
@login_matcher.handle()
async def _(state: T_State):
    if (username is not None) and (password is not None):
        cli, img = await get_checkcode()
        state["client"] = cli
        await login_matcher.send("请尽快输入验证码，以免失效" + MessageSegment.image(img))
    else:
        await login_matcher.finish("缺少账号或密码！")


# 获取验证码
@login_matcher.got(key="checkcode")
async def _(state: T_State, checkcode: Message = Arg("checkcode")):
    global client, login_state

    checkcode = str(checkcode)
    cli = state["client"]
    info = await login(cli, username, password, checkcode)

    if info[0] is False:
        await login_matcher.finish(f"登录失败:{info[1]}将以启动时状态继续")

    client = info[1]
    client.follow_redirects = True
    user_info = await client.get(url="https://w.linovelib.com/user.php")
    nickname = re.findall(r'<span class="user-name">(?P<username>.*?)</span>', user_info.text)[0]
    login_state = True
    await login_matcher.finish(f"登录成功，{nickname}")


# 获取cookies
@cookies_matcher.handle()
async def _():
    driver.get(r"https://w.linovelib.com/search.html")
    await sleep(2)
    cookies = driver.get_cookies()
    for cookie in cookies:
        client.cookies.set(cookie["name"], cookie["value"])
    await cookies_matcher.finish("成功获取cookies！")


# 使用id
@id_matcher.handle()
async def _(state: T_State, nid: Message = CommandArg()):
    try:
        nid = int(str(nid))
    except ValueError:
        await id_matcher.finish("请输入正确的书页ID！", at_sender=True)
    else:
        await book_matcher.send("请稍后......", at_sender=True)

    book_url = f"https://w.linovelib.com/novel/{nid}.html"
    book_info = (await client.get(url=book_url)).text
    state["book_url"] = book_url
    pic = await get_content(book_info)
    await book_matcher.send(MessageSegment.image(pic), at_sender=True)


@id_matcher.got("prompt")
async def _(state: T_State, pmt: Message = Arg("prompt")):
    pmt = str(pmt)
    if pmt != "index" and pmt != "index_tree":
        await id_matcher.finish("选择取消", at_sender=True)
    else:
        state["mode"] = pmt
        await id_matcher.skip()


# 使用书名
@book_matcher.handle()
async def _(state: T_State, name: Message = CommandArg()):
    await id_matcher.send("正在搜索中，请耐心等待......", at_sender=True)

    res = await search(client=client, name=name, retry_num=retry_num)

    if res:
        if res[0] == "book_page":
            book_info = res[1]
            book_url = res[2]
            pic = await get_content(book_info)
            state["book_url"] = book_url
            await book_matcher.send(MessageSegment.image(pic), at_sender=True)
        else:
            book_list, url_list = res
            state["url_list"] = url_list
            state["book_list"] = book_list
            book_info = "\n".join([f"{num + 1}.{book}" for num, book in enumerate(book_list)])

            try:
                await book_matcher.send(book_info, at_sender=True)
            except ActionFailed:
                await book_matcher.finish(f"发送失败！", at_sender=True)

    else:
        logger.warning(Fore.LIGHTYELLOW_EX + "搜索失败，请使用nvl_cookies指令自动获取cookies")
        await book_matcher.finish("搜索失败！", at_sender=True)


@bookcase_matcher.handle()
async def _(state: T_State):
    result = await get_bookcase(client)

    if result is not False:
        book_list, url_list = result
        state["url_list"] = url_list
        state["book_list"] = book_list
        book_info = "\n".join([f"{num + 1}.{book}" for num, book in enumerate(book_list)])

        try:
            await book_matcher.send(book_info, at_sender=True)
        except ActionFailed:
            await book_matcher.send(f"发送失败，Bot可能被风控或结果太多，尝试发送前{retry_num}条", at_sender=True)
            try:
                book_info = "\n"
                for i in range(retry_num):
                    book_info += f"{i + 1}.{book_list[i]}\n"
                await book_matcher.send(book_info, at_sender=True)
            except ActionFailed:
                await book_matcher.send(f"发送失败，Bot可能被风控", at_sender=True)
    else:
        await book_matcher.finish('当前为未登录状态，获取书架失败！', at_sender=True)


# 使用序号查询
@book_matcher.got(key="cmd")
@bookcase_matcher.got(key="cmd")
async def _(matcher: Matcher, state: T_State, cmd: Message = Arg("cmd")):
    cmd = str(cmd)
    try:
        cmd = int(cmd)
    except ValueError:
        if cmd != "index" and cmd != "index_tree":
            await matcher.finish("选择取消", at_sender=True)
        else:
            try:
                state["book_url"] = state["url_list"][state["order"]]
            except KeyError:
                pass
            del state["url_list"]
            state["mode"] = cmd
            await matcher.skip()

    state["order"] = cmd - 1
    book_url = state["url_list"][cmd - 1]
    await matcher.send("请稍后......", at_sender=True)

    book_info = (await client.get(url=book_url)).text
    pic = await get_content(book_info)

    await matcher.reject(MessageSegment.image(pic), at_sender=True)


# 发送目录
@id_matcher.handle()
@book_matcher.handle()
@bookcase_matcher.handle()
async def _(matcher: Matcher, state: T_State):
    book_url = state["book_url"]
    try:
        aid = re.findall(r'aid=(\d+)', book_url)[0]
    except IndexError:
        aid = re.findall(r'/novel/(\d+)\.', book_url)[0]

    index_url = f"https://w.linovelib.com/novel/{aid}/catalog"
    index_info = (await client.get(index_url)).text
    index_dict = await index_parse(index_info)

    state["index_dict"] = index_dict

    if state["mode"] == "index":
        chapters = "\n".join(index_dict.keys())
        await matcher.send(chapters, at_sender=True)

    await matcher.skip()


@id_matcher.handle()
@book_matcher.handle()
@bookcase_matcher.handle()
async def _(state: T_State, matcher: Matcher):
    if state["mode"] == "index":
        matcher.skip()

    elif state["mode"] == "index_tree":
        index_dict = state["index_dict"]
        html_path = html_parse(index_dict=index_dict)

        driver.get(f'file:///{html_path}')
        if browser != "phantomjs":
            browser_size_reset()
        pic = driver.get_screenshot_as_png()

        await matcher.finish(MessageSegment.image(pic), at_sender=True)


@id_matcher.got("chapter")
@book_matcher.got("chapter")
@bookcase_matcher.got("chapter")
async def _(matcher: Matcher, state: T_State, chapter: Message = Arg("chapter")):
    chapter = str(chapter)
    index_dict = state["index_dict"]
    try:
        episodes = index_dict[chapter]
    except KeyError:
        await matcher.finish("选择取消", at_sender=True)

    html_path = html_parse(chapter=chapter, episodes=episodes)

    driver.get(f'file:///{html_path}')
    if browser != "phantomjs":
        browser_size_reset()
    pic = driver.get_screenshot_as_png()

    await matcher.reject(MessageSegment.image(pic), at_sender=True)
