# -*- coding: utf-8 -*-
from nonebot.adapters.onebot.v11 import GROUP, PRIVATE_FRIEND, Message, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from nonebot import on_command
from nonebot.exception import ActionFailed
from nonebot import require
from nonebot.params import Arg, T_State, CommandArg

from colorama import init, Fore
from .config import username, password, retry_num, cookie
from .work import *

require("nonebot_plugin_htmlrender")

__version__ = "0.1.1"

login_matcher = on_command(cmd="nvl_login", priority=5, permission=SUPERUSER, block=True)
book_matcher = on_command(cmd="nvl", priority=5, permission=GROUP | PRIVATE_FRIEND, block=True)

# 初始请求状态
login_state = False
client = AsyncClient(
    headers={
        "origin": "https://w.linovelib.com",
        "User-Agent": UserAgent().random
    },
    timeout=None,
    follow_redirects=True
)
if cookie is None:
    cookie_path = path.join(path.abspath(path.dirname(__file__)), "cookie.txt")
    try:
        with open(file=cookie_path, mode="r", encoding="utf-8") as f:
            cookie = f.read()
    except FileNotFoundError:
        login_state = False
        logger.warning(Fore.LIGHTYELLOW_EX + "将以未登录状态继续")
    else:
        client.headers["cookie"] = cookie
        login_state = True
        logger.info(Fore.LIGHTCYAN_EX + "使用自动保存的cookie继续")
else:
    login_state = True
    logger.info(Fore.LIGHTCYAN_EX + "使用light_nvl_cookie配置项cookie继续")
    client.headers["cookie"] = cookie

# 字体样式初始化（自动重设字体样式）
init(autoreset=True)

logger.success(Fore.LIGHTGREEN_EX + f"成功导入本插件，插件版本为{__version__}")


@login_matcher.handle()
async def _(state: T_State, prompt: Message = CommandArg()):
    prompt = str(prompt)
    if (login_state is True) and ("enforce" not in prompt):
        user_info = await client.get(url="https://w.linovelib.com/user.php")
        nickname = re.findall(r'<span class="user-name">(?P<username>.*?)</span>', user_info.text)[0]
        await login_matcher.finish(f"已登录！当前账号为 {nickname}")
    # 登录获取client
    if (username is not None) and (password is not None):
        cli, img = await get_checkcode()
        state["client"] = cli
        await login_matcher.send("请尽快输入验证码，以免失效" + MessageSegment.image(img))
    else:
        await login_matcher.finish("缺少账号或密码，将以未登录状态继续")


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


@book_matcher.handle()
async def _(state: T_State, name: Message = CommandArg()):
    name = str(name)

    if "id" in name:
        try:
            book_id = re.findall(r'(\d+)', name)[0]
        except IndexError:
            await book_matcher.finish("输入有误！", at_sender=True)
        else:
            book_url = f"https://w.linovelib.com/novel/{book_id}.html"
            state["book_url"] = book_url
            state["decorator"] = "handel"
    else:
        state["decorator"] = "got"
        if "bookcase" in name:
            if login_state is True:
                result = await get_bookcase(client)
            else:
                result = None
                await book_matcher.finish("当前为未登录状态，无法使用此功能", at_sender=True)
        else:
            result = await search(client, name, retry_num)

        if result is not False:
            book_list, url_list = result
            state["url_list"] = url_list
            num = 0
            book_info = "\n"
            for book in book_list:
                num += 1
                book_info += f"{num}.{book}\n"

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
            await book_matcher.finish(fr'失败！', at_sender=True)


@book_matcher.handle()
async def _(state: T_State):
    if state["decorator"] == "got":
        await book_matcher.skip()

    book_url = state["book_url"]
    pic, index_url, book_id = await get_content(client, book_url)
    await book_matcher.send(MessageSegment.image(pic))


@book_matcher.got(key="order")
async def _send_content(state: T_State, order: Message = Arg("order")):
    if state['decorator'] == "handle":
        await book_matcher.finish()
    order = str(order)
    try:
        order = int(order)
    except ValueError:
        await book_matcher.finish()
    book_url = state["url_list"][order - 1]

    pic, index_url, book_id = await get_content(client, book_url)

    await book_matcher.send(MessageSegment.image(pic))
