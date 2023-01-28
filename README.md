# :memo: nonebot_plugin_zyk_lightNVL

*:page_facing_up: 使用本插件前请仔细阅读README*

*本插件基于轻小说网站[哔哩轻小说](https://w.linovelib.com)制作*

>说明

本插件目前只是半成品，先厚脸皮来占个坑。

目前只支持查询的功能，后面会支持下载。

为什么不做完再发？因为~~懒~~没时间在短期内完成。

## :cd: 安装方式
- #### 使用pip
```
pip install nonebot_plugin_zyk_lightNVL
```
- #### 使用nb-cli
```
nb plugin install nonebot_plugin_zyk_lightNVL
```

## :wrench: env配置

第一次启动时账号密码和cookie二者必须有一个

|        Name         |   Example   | Type |      Usage       | Required |
|:-------------------:|:-----------:|:----:|:----------------:|:--------:|
| light_nvl_username  |     cxk     | str  |   哔哩轻小说账户的用户名    |    No    |
| light_nvl_password  |   123456    | str  |    哔哩轻小说账户的密码    |    No    |
|  light_nvl_cookie   | your:cookie | str  |   已经登录的cookie    |    No    |
| light_nvl_retry_num |     50      | int  | 搜索结果发送失败时重新发送的条数 |    No    |

### 登录说明
未登录状态下能使用的功能可能受限，推荐先去[网站](https://w.linovelib.com/register.php)注册一个账号再搭配本插件食用。

每次启动时会优先使用env中配置的cookie，如果没有则使用自动保存的cookie登录，如果也没有则以未登录状态继续。

第一次启动则没有自动保存的cookie，需要使用指令来手动登录。

每次手动登录成功后将会自动保存cookie。

如果已经在浏览器中登录过了，可以直接复制cookie到env配置项中。

在有cookie的情况下，无法手动登录。可以使用手动登录指令的*enforce*参数来强制手动登录，一般用于切换账号或cookie异常的情况。


## :label: 指令
### 手动登录
```
(COMMAND_START)nvl_login [enforce]

eg:
    /nvl_login
```
- 可选参数*enforce*用于强制手动登录
```
/nvl_login enforce
```

### 操作
```
(COMMAND_START)nvl [(info)|bookcase|id (book_id)]

eg:
    /nvl 回复术士
```

- 可选参数 *(info)* 、*bookcase*、*id (book_id)* 中**请确保有一个参数存在**。

1. *(info)* 用于查找轻小说，可以是书名、作者、或类型等。

2. *bookcase* 用于查看当前账号的书架，只有登录状态才可以使用。

3. *id (book_id)* 用于导入book_id（可以在书的网址中查看，如 `https://w.linovelib.com/novel/3518.html` 中的 `3518`）

---

:bug: 如果发现插件有BUG或有建议，欢迎**合理**提*Issue*

:heart: 最后，如果你喜欢本插件，就请给本插件点个:star:吧