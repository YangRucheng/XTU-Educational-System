"""
# 强智教务系统爬虫模块
 仅在湘潭大学教务系统测试成功

### 爬虫class
+ `Login` 登陆(基类)
+ `CourseTable` 爬课表表
+ `EmptyClassroom` 爬空教室表
+ `Examination` 爬考试表

![头像图片](https://www.yangrucheng.top/favicon.ico)
作者: YangRucheng
[作者主页](https://www.yangrucheng.top) [论坛讨论](https://forum.yangrucheng.top)

本模块仅用于Python学习, 不得用于非法用途  
Apache License 2.0
"""

from .登陆 import Login
from .培养方案 import Scheme, Subject
from .课表 import CourseTable, Course
from .考试 import Examination, ExamSubject
from .空教室 import EmptyClassroom, Classroom
