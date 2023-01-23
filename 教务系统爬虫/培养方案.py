from bs4 import BeautifulSoup
from urllib import parse
from .登陆 import Login
import asyncio


class Subject(object):
    """ 学科 """
    序号: str
    开设学期: str
    课程名称: str
    课程号: str
    课程类别: str
    总学时: str
    学分: str
    考核方式: str

    def __init__(self, data: dict = None) -> None:
        if type(data) == dict:
            self.序号 = data.get('序号')
            self.开设学期 = data.get('开设学期')
            self.课程名称 = data.get('课程名称')
            self.课程号 = data.get('课程号')
            self.课程类别 = data.get('课程类别')
            self.总学时 = data.get('总学时')
            self.学分 = data.get('学分')
            self.考核方式 = data.get('考核方式')

    def __iter__(self) -> dict:
        yield "序号", self.序号,
        yield "开设学期", self.开设学期,
        yield "课程名称", self.课程名称,
        yield "课程号", self.课程号,
        yield "课程类别", self.课程类别,
        yield "总学时", self.总学时,
        yield "学分", self.学分,
        yield "考核方式", self.考核方式

    def __str__(self) -> str:
        return str(dict(self))

    def __repr__(self) -> str:
        return str(dict(self))


class Scheme(Login):
    """ 培养方案爬虫 """
    __属性映射: list[str] = [
        "序号", "开设学期", "课程名称", "课程号", "课程类别", "总学时", "学分", "考核方式"]
    培养方案: list[Subject] = []
    培养方案JSON: list[dict] = []

    async def __accessSchemeHTML(self) -> str:
        """ 访问培养方案页面, 返回HTML """
        url = parse.urljoin(self.url, "jsxsd/pyfa/pyfazd_query")
        resp = await self.client.get(url=url, headers=self.headers, cookies=self.cookies)
        return resp.text

    def __analysisHTML(self, html) -> list:
        """ 解析HTML """
        soup = BeautifulSoup(html, 'html.parser')
        培养方案表 = soup.find('table', id="dataList")
        所有学科 = 培养方案表.find_all('tr')[1:]
        for 学科 in 所有学科:
            全部属性 = 学科.find_all('td')
            data: dict = {}
            for index in range(len(全部属性)):
                data |= {self.__属性映射[index]: 全部属性[index].next_element.strip()}
            self.培养方案.append(Subject(data))
            self.培养方案JSON.append(data)
        return self.培养方案

    async def __call__(self) -> list[Subject]:
        """ 登陆, 并返回培养方案 """
        await super().__call__()
        return self.__analysisHTML(await self.__accessSchemeHTML())
