# :memo: nonebot_plugin_zyk_lightNVL

*:page_facing_up: 使用本插件前请仔细阅读README*

*本插件基于轻小说网站[哔哩轻小说](https://w.linovelib.com)制作*

## 更新0.2.0

1. 解决网站cookies问题
2. 取消依赖nonebot_plugin_htmlrender，适配windows7
3. 优化交互方式，可连续交互

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

|        Name         |   Example   | Type |      Usage       | Required |
|:-------------------:|:-----------:|:----:|:----------------:|:--------:|
| light_nvl_username  |     cxk     | str  |   哔哩轻小说账户的用户名    |    No    |
| light_nvl_password  |   123456    | str  |    哔哩轻小说账户的密码    |    No    |
|  light_nvl_show_all   | False | bool  |   是否显示所有搜索结果，建议为False    |    No    |
| light_nvl_retry_num |     50      | int  | 搜索结果发送失败时重新发送的条数 |    No    |

### 登录说明

[账号注册](https://w.linovelib.com/register.php)

启动前请先在浏览器中访问[搜索页面](https://w.linovelib.com/search.html)以确保能够自动获取cookies

## :label: 指令

### 登录

```
(COMMAND_START)nvl_login

eg:
    /nvl_login
```

### 刷新cookies
```
(COMMAND_START)nvl_cookies

eg:
    /nvl_cookies
```

用于cookies过期的情况，可能会失效。如果失效请重启bot以刷新

### 查找轻小说

#### 使用关键字查找

```
(COMMAND_START)nvl (key words)

eg:
    /nvl 回复术士
```

#### 使用书页id精确查找

```
(COMMAND_START)nvl_id (id)

eg:
    /nvl_id 3636
```

#### 个人书架

```
(COMMAND_START)nvl_bookcase

eg:
    /nvl_bookcase
```

只有登录后才可使用

---

:bug: 如果发现插件有BUG或有建议，欢迎**合理**提*Issue*

:heart: 最后，如果你喜欢本插件，就请给本插件点个:star:吧
