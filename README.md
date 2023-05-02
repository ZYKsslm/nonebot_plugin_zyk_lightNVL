# :memo: nonebot_plugin_zyk_lightNVL

*:page_facing_up: 使用本插件前请仔细阅读README*

*本插件基于轻小说网站[哔哩轻小说](https://w.linovelib.com)制作*

## 更新0.3.0

1. 可选使用chorme浏览器工作，速度更快，渲染更优
2. 新增查看小说目录功能（爆肝中）

## :cd: 安装方式

- #### 使用pip

```cmd
pip install nonebot_plugin_zyk_lightNVL
```

- #### 使用nb-cli

```cmd
nb plugin install nonebot_plugin_zyk_lightNVL
```

## :wrench: env配置

|        Name         |   Example   | Type |      Usage       | Required |
|:-------------------:|:-----------:|:----:|:----------------:|:--------:|
| light_nvl_username  |     cxk     | str  |   哔哩轻小说账户的用户名    |    No    |
| light_nvl_password  |   123456    | str  |    哔哩轻小说账户的密码    |    No    |
|  light_nvl_show_all   | False | bool  |   是否显示所有搜索结果，建议为False    |    No    |
| light_nvl_retry_num |     50      | int  | 搜索结果发送失败时重新发送的条数 |    No    |
| light_nvl_browser | chrome | str | 选择的浏览器，默认phantomjs，可选chrome | No |
| light_nvl_chromedriver_path | path/to/your/chromedriver | str | chromedriver的绝对路径，版本要与你的chrome浏览器一致 | No |

### 登录说明

[账号注册](https://w.linovelib.com/register.php)

获取cookies:

- 启动前先在浏览器中访问[搜索页面](https://w.linovelib.com/search.html)
- 使用nvl_cookies指令

## :label: 指令

### 登录

```cmd
(COMMAND_START)nvl_login

eg:
    /nvl_login
```

### 自动获取cookies

```cmd
(COMMAND_START)nvl_cookies

eg:
    /nvl_cookies
```

用于cookies过期的情况，如果失效请再试一次或重启bot以刷新

### 查找轻小说

#### 使用关键字查找

```cmd
(COMMAND_START)nvl (key words)

eg:
    /nvl 回复术士
```

#### 使用书页id精确查找

```cmd
(COMMAND_START)nvl_id (id)

eg:
    /nvl_id 3636
```

#### 个人书架

```cmd
(COMMAND_START)nvl_bookcase

eg:
    /nvl_bookcase
```

只有登录后才可使用

### 查看目录

在bot给你发送了小说的详细信息（一张图片）之后，可以发送`index`和`index_tree`让bot给你发送该小说的目录

- index

用于发送小说的卷数，可进行下一级交互和重复交互

- index_tree

用于发送小说的全部章节（卷数和章数），不可进行下一级交互或重复交互

---

:bug: 如果发现插件有BUG或有建议，欢迎**合理**提*Issue*

:heart: 最后，如果你喜欢本插件，就请给本插件点个:star:吧
