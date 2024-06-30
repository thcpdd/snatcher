# 系统核心模块

---

### 模块概览

整个核心模块主要分为以下几个部分：

1. 课程选择器模块
2. 数据存储模块
3. 邮件发送模块
4. 用户会话模块
5. 任务调度模块

下面分别详细的介绍这几个模块。

### 课程选择器模块

这个是模块是整个项目最最重要的模块，因为它实现了完整的选课流程。

在这个模块中，实现了一些课程选择器类。每个课程选择器以“类”的形式存在，通过面向的封装继承多态，大大的提高了代码的复用性。

##### 课程选择器基类

位于：`./selector/base.py`下。

这个“类”是所有课程选择器的“抽象类”，它定义了一个标准的课程选择器应该具有的**属性**。

这里对每一个属性进行说明：

|         属性名称          | 属性类别 |                             说明                             |
| :-----------------------: | :------: | :----------------------------------------------------------: |
|       `course_type`       |  类属性  |       区分每个课程选择器的选课类别（需要在子类中重写）       |
|          `term`           |  类属性  |                指定了选课的学期（上、下学期）                |
|   `select_course_year`    |  类属性  |                       指定了选课的年份                       |
|        `username`         | 实例属性 |                          学生的学号                          |
|    `get_jxb_ids_data`     | 实例属性 |                 用于获取`jxb_ids`的表单数据                  |
|   `select_course_data`    | 实例属性 |               用于向选课接口发送请求的表单数据               |
|         `timeout`         | 实例属性 |              从发送请求到接收响应的**最长时间**              |
|  `sub_select_course_api`  | 实例属性 |       选课接口的**子接口**，用于拼接**完整的选课接口**       |
|      `sub_index_url`      | 实例属性 |     选课首页的**子链接**，用于拼接**完整的选课首页链接**     |
|     `sub_jxb_ids_api`     | 实例属性 | 获取`jxb_ids`的**子接口**，用于拼接获取`jxb_ids`的**完整接口** |
|    `select_course_api`    | 实例属性 |                        完整的选课接口                        |
|        `index_url`        | 实例属性 |                       选择选课首页链接                       |
|       `jxb_ids_api`       | 实例属性 |                  完整的获取`jxb_ids`的接口                   |
|         `logger`          | 实例属性 |                          日志记录器                          |
|        `real_name`        | 实例属性 |                        真实的课程名字                        |
|       `logger_key`        | 实例属性 |                         日志器的名字                         |
|         `session`         | 实例属性 |                        发送请求的会话                        |
|     `session_manager`     | 实例属性 |            管理该选择器对应学生学号的所有会话信息            |
|         `cookies`         | 实例属性 |                    用于模拟登录的`Cookie`                    |
|        `base_url`         | 实例属性 |                   用于拼接所有的接口或链接                   |
|          `port`           | 实例属性 |                  当前接口或链接对应的主机号                  |
|         `kch_id`          | 实例属性 |                           课程号ID                           |
|         `jxb_ids`         | 实例属性 |                           教学班ID                           |
|         `xkkz_id`         | 实例属性 |           （想不出中文名，用于发送请求的重要参数）           |
| `latest_selected_data_id` | 实例属性 |    已选课程记录`ID`，该属性记录了上一条数据库表记录的`ID`    |

##### 课程选择器类

位于：`./selector/base.py`下。

所有课程选择器的父类，所有的课程选择器都应该继承于该类，而不是课程选择器基类。它在基类的基础上，定义了课程选择器应该实现的所有方法。

这里对每一个方法进行说明：

|        方法名称         |                         方法作用                          |
| :---------------------: | :-------------------------------------------------------: |
|      `set_xkkz_id`      |            为该选择器类设置一个有效的`xkkz_id`            |
|      `set_jxb_ids`      |            为该选择器类设置一个有效的`jxb_ids`            |
| `prepare_for_selecting` |         依次调用`set_xkkz_id`和`set_jxb_ids`方法          |
|   `simulate_request`    | 在内部调用`prepare_for_selecting`方法并向选课接口发送请求 |
|        `select`         |          外部调用者应该调用这个方法来启动选择器           |
| `update_or_set_cookie`  |             设置新的`Cookie`和`所有请求链接`              |
| `update_selector_info`  |     更换当前选择器的选课信息（课程名称、课程号ID等）      |
|      `mark_failed`      |                   标记当前选课任务失败                    |

##### 异步课程选择器类

位于：`./selector/async_selector.py`下。

继承于`课程选择器类`并实现了绝大部分的选课逻辑。所有发送请求的方式都是异步的。

##### 异步公选课课程选择器类

位于：`./selector/async_selector.py`下。

继承于`异步课程选择器类`，实现了公选课的完整选课逻辑。

##### 异步体育课课程选择器类

位于：`./selector/async_selector.py`下。

继承于`异步课程选择器类`，实现了体育课的完整选课逻辑。

##### 同步课程选择器类（已弃用）

位于：`./selector/sync_selector.py`下。

继承于`课程选择器类`并实现了绝大部分的选课逻辑。所有发送请求的方式都是同步的。

##### 同步公选课课程选择器类（已弃用）

位于：`./selector/sync_selector.py`下。

继承于`同步课程选择器类`，实现了公选课的完整选课逻辑。

##### 同步体育课课程选择器类（已弃用）

位于：`./selector/sync_selector.py`下。

继承于`同步课程选择器类`，实现了体育课的完整选课逻辑。

### 数据存储模块

该模块提供了一系列的类或函数用于实现与数据库之间的数据交互。

##### 数据持久化模块

位于：`./storage/mysql.py`下。

在该模块中，定义了一系列的函数或类，用于实现与数据之间的交互。

|     类名 / 函数名 / 方法名 / 实例名      |                             作用                             |
| :--------------------------------------: | :----------------------------------------------------------: |
|           `get_db_connection`            |       从配置文件中读取数据库的配置并返回一个数据库连接       |
|               `SQLQuerier`               |  所有查询器的父类，允许用户通过调用对应的方法名来操作数据库  |
|     `SQLQuerier._ensure_connecting`      |              确保当前`SQL`查询器的连接是有效的               |
|           `SQLQuerier.execute`           |               执行`SQL`语句并返回一个游标对象                |
|     `SQLQuerier.parse_query_result`      |       解析查询结果，返回一个可用于序列化的`Python`对象       |
|     `SQLQuerier.parse_count_result`      | 解析统计行记录数量后的结果，返回一个可用于序列化的`Python`对象 |
|      `SQLQuerier.pagination_query`       |                           分页查询                           |
|            `SQLQuerier.count`            |              根据条件统计当前数据库表的行记录数              |
|               `PCQuerier`                |                         公选课查询器                         |
|            `PCQuerier.insert`            |                  向公选课数据中插入一条记录                  |
|          `PCQuerier.like_query`          |                  在公选课数据中进行模糊查询                  |
|               `PEQuerier`                |                         体育课查询器                         |
|            `PEQuerier.insert`            |                  向体育课数据中插入一条记录                  |
|          `PEQuerier.like_query`          |                  在体育课数据中进行模糊查询                  |
|           `FailedDataQuerier`            |                      选课失败数据查询器                      |
|        `FailedDataQuerier.insert`        |                向选课失败的数据中插入一条记录                |
|       `SelectedCourseDataQuerier`        |                      已选课程数据查询器                      |
|    `SelectedCourseDataQuerier.insert`    |                 向已选课程数据中插入一条记录                 |
| `SelectedCourseDataQuerier.mark_success` |                 标记该条已选课程数据选课成功                 |
|           `VerifyCodesQuerier`           |                       抢课码数据查询器                       |
|       `VerifyCodesQuerier.insert`        |                  向抢课码数据中插入一条记录                  |
|        `VerifyCodesQuerier.query`        |               查询某个学生某个抢课码的使用情况               |
|       `VerifyCodesQuerier.update`        |                    标记指定抢课码已被使用                    |
|               `pc_querier`               |                    公选课课程查询器的实例                    |
|               `pe_querier`               |                    体育课课程查询器的实例                    |
|               `fd_querier`               |                   选课失败数据查询器的实例                   |
|              `scd_querier`               |                   已选课程数据查询器的实例                   |
|               `vc_querier`               |                    抢课码数据查询器的实例                    |

##### 数据缓存模块

位于：`./storage/cache.py`下。

该模块提供了一系列的函数或类与`Redis`进行交互。

|  变量名 / 类名 / 函数名  |                   作用                   |
| :----------------------: | :--------------------------------------: |
|    `USING_CODES_NAME`    | 正在使用的抢课码会保存在这个名字的缓存中 |
|      `CHANNEL_NAME`      |             发布消息的频道名             |
|      `public_cache`      |        公共缓存的`Redis`的连接池         |
|   `mark_code_is_using`   |        将目标抢课码标记为正在使用        |
|  `remove_code_is_using`  |          将正在使用的抢课码移除          |
|  `judge_code_is_using`   |          判断抢课码是否正在使用          |
|    `publish_message`     | 一个装饰器，用于向指定频道中发布一条消息 |
|     `parse_message`      |       将频道中的消息解析成字典格式       |
|   `AsyncRuntimeLogger`   |    一个上下文管理器，运行时日志记录器    |
| `runtime_logs_generator` |   运行时日志生成器，生成所有运行时日志   |

### 用户会话模块

位于：`./session.py`下。

在该模块下，为用户会话的设置与修改提供了一系列的类或函数。

|            类名 / 函数名            |                  说明                  |
| :---------------------------------: | :------------------------------------: |
|          `SessionManager`           |   会话管理器，管理指定学号的会话信息   |
|        `SessionManager.get`         |        获取指定主机号的会话信息        |
|    `SessionManager.save_cookie`     |        为指定主机号保存会话信息        |
|    `SessionManager.save_xkkz_id`    |             保存`xkkx_id`              |
|    `SessionManager.get_xkkz_id`     |             获取`xkkx_id`              |
|    `SessionManager.all_sessions`    |       获取当前学号的所有会话信息       |
|    `SessionManager.has_sessions`    |       判断当前学号是否有会话信息       |
|    `SessionManager.has_session`     | 判断当前学号是否有某个主机号的会话信息 |
| `SessionManager.get_random_session` |  从所有会话信息中随机获取一个会话信息  |
|       `SessionManager.close`        |               关闭连接池               |
|        `get_session_manager`        |     获取并返回一个学号的会话管理器     |
|        `AsyncSessionSetter`         | 异步会话设置器，模拟登录并获取会话信息 |
|         `async_set_session`         |   调用异步会话设置器，并保存会话信息   |
|    `async_check_and_set_session`    |             检查并设置会话             |

### 邮件发送模块

位于：`./postman/mail.py`下。

封装了发送邮件的快捷方式。这里就不多介绍了。

### 任务调度模块

位于：`./aiotasks.py`下。

该模块基于`aiocelery`实现了异步定时任务队列，所有的选课任务都将提交到该任务队列中，并由`Celery-Worker`不断将任务取出并执行。

