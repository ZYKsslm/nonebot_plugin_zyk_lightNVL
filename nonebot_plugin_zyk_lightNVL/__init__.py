# -*- coding: utf-8 -*-
from nonebot.adapters.onebot.v11 import GROUP, PRIVATE_FRIEND, Message, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from nonebot import on_command
from nonebot.exception import ActionFailed
from nonebot.params import Arg, T_State, CommandArg

from colorama import init, Fore
from .work import *

__version__ = "0.2"

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


#重新获取cookies
@cookies_matcher.handle()
async def _():
    cookies = reset_cookies()
    client.cookies = cookies
    await cookies_matcher.finish("成功获取cookies！")


# 使用id
@id_matcher.handle()
async def _(nid: Message = CommandArg()):
    try:
        nid = int(str(nid))
    except ValueError:
        await id_matcher.finish("请输入正确的书页ID！", at_sender=True)
    else:
        await book_matcher.send("请稍后......", at_sender=True)

    book_info = (await client.get(url=f"https://w.linovelib.com/novel/{nid}.html")).text
    pic = await get_content(book_info)
    await book_matcher.send(MessageSegment.image(pic), at_sender=True)


# 使用书名
@book_matcher.handle()
async def _(state: T_State, name: Message = CommandArg()):
    await id_matcher.send("正在搜索中，请耐心等待......")

    res = await search(client=client, name=name, retry_num=retry_num)

    if res:
        if res[0] == "book_page":
            book_info = res[1]
            pic = await get_content(book_info)
            await book_matcher.finish(MessageSegment.image(pic), at_sender=True)
        else:
            book_list, url_list = res
            state["url_list"] = url_list
            book_info = "\n".join([f"{num+1}.{book}" for num, book in enumerate(book_list)])

            try:
                await book_matcher.send(book_info, at_sender=True)
            except ActionFailed:
                await book_matcher.send(f"发送失败！", at_sender=True)
    else:
        logger.warning(Fore.LIGHTYELLOW_EX + "搜索失败，请尝试在浏览器中访问https://w.linovelib.com/search.html后使用nvl_cookies指令或重启bot")
        await book_matcher.finish("搜索失败！", at_sender=True)


@book_matcher.got(key="order")
async def _(state: T_State, order: Message = Arg("order")):
    order = str(order)
    try:
        order = int(order)
    except ValueError:
        await book_matcher.finish("选择取消", at_sender=True)

    book_url = state["url_list"][order - 1]
    await book_matcher.send("请稍后......", at_sender=True)

    book_info = (await client.get(url=book_url)).text
    pic = await get_content(book_info)

    await book_matcher.send(MessageSegment.image(pic))
    await book_matcher.reject()


@bookcase_matcher.handle()
async def _(state: T_State):
    result = await get_bookcase(client)

    if result is not False:
        book_list, url_list = result
        state["url_list"] = url_list
        book_info = "\n".join([f"{num+1}.{book}" for num, book in enumerate(book_list)])

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


@bookcase_matcher.got(key="order")
async def _(state: T_State, order: Message = Arg("order")):
    order = str(order)
    try:
        order = int(order)
    except ValueError:
        await book_matcher.finish("选择取消", at_sender=True)

    book_url = state["url_list"][order - 1]
    await book_matcher.send("请稍后......", at_sender=True)

    book_info = (await client.get(url=book_url)).text
    pic = await get_content(book_info)

    await book_matcher.send(MessageSegment.image(pic))
    await book_matcher.reject()