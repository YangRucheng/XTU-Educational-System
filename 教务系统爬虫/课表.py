from bs4 import BeautifulSoup
from urllib import parse
from .登陆 import Login
import asyncio
from typing import Dict


class Course(object):
    """ 课程对象 """
    课程名 = ""
    教师 = ""
    周次 = ""
    教室 = ""
    节次 = ""
    星期 = ""

    def __iter__(self) -> dict:
        yield "课程名", self.课程名,
        yield "教师", self.教师,
        yield "周次", self.周次,
        yield "教室", self.教室,
        yield "节次", self.节次,
        yield "星期", self.星期

    def __str__(self) -> str:
        return str(dict(self))

    def __repr__(self) -> str:
        return str(dict(self))


class CourseTable(Login):
    """ 课表爬虫 """
    __星期映射: list = [
        "周一", "周二", "周三",  "周四",  "周五",  "周六",  "周日"]
    课表: Dict[list[Course]] = {
        "周一": [], "周二": [], "周三": [],
        "周四": [], "周五": [], "周六": [],
        "周日": []
    }
    课表JSON: Dict[list[dict]] = {
        "周一": [], "周二": [], "周三": [],
        "周四": [], "周五": [], "周六": [],
        "周日": []
    }
    备注: str = ""
    周次: str = ""

    async def __accessCouresHTML(self) -> str:
        """ 访问课表页面, 返回HTML """
        url = parse.urljoin(self.url, "jsxsd/xskb/xskb_list.do")
        data = {'xnxq01id': self.学期, 'zc': self.周次}
        resp = await self.client.post(url=url, headers=self.headers, data=data, cookies=self.cookies)
        return resp.text

    def __analysisHTML(self, html) -> dict:
        """ 解析HTML到类属性 """
        soup = BeautifulSoup(html, 'html.parser')
        课表 = soup.find('table', id="kbtable")
        self.备注 = 课表.find_all('tr')[6].find('td').contents[0]
        所有节次课表 = 课表.find_all('tr')[1:6]  # 按节次放入列表的课表
        for 节次 in 所有节次课表:
            节次编号 = 节次.find('th').next_element.strip()  # 节次编号
            当前节次的所有课表 = 节次.find_all('td')  # 当前节次的每日课表
            for 星期 in range(7):
                course = Course()
                课程 = 当前节次的所有课表[星期].find('div', class_='kbcontent')
                course.课程名 = 课程.contents[0].strip()
                所有属性 = 课程.find_all('font')
                for 属性 in 所有属性:
                    if "老师" in 属性['title']:
                        course.教师 = 属性.contents[0].strip()
                    elif "周次" in 属性['title']:
                        course.周次 = 属性.contents[0].strip()
                    elif "教室" in 属性['title']:
                        course.教室 = 属性.contents[0].strip()
                course.星期 = self.__星期映射[星期]
                course.节次 = 节次编号
                if course.课程名:  # 不为空
                    self.课表[self.__星期映射[星期]].append(course)
        return self.课表

    async def __call__(self, week: str = "") -> dict:
        """ 获取课表 """
        if await self.checkLogin() == False:
            await super().__call__()
        self.周次 = week
        return self.__analysisHTML(await self.__accessCouresHTML())
