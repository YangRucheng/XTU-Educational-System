from bs4 import BeautifulSoup
from urllib import parse
from .登陆 import Login
import asyncio


class ExamSubject(object):
    """ 考试科目 """
    序号: str
    考试场次: str
    课程名称: str
    考核方式: str
    考试形式: str
    考试时间: str
    考场: str
    座位号: str
    准考证号: str
    备注: str
    操作: str

    def __init__(self, data: dict = None) -> None:
        if type(data) == dict:
            self.序号 = data.get('序号')
            self.考试场次 = data.get('考试场次')
            self.课程名称 = data.get('课程名称')
            self.考核方式 = data.get('考核方式')
            self.考试形式 = data.get('考试形式')
            self.考试时间 = data.get('考试时间')
            self.考场 = data.get('考场')
            self.座位号 = data.get('座位号')
            self.准考证号 = data.get('准考证号')
            self.备注 = data.get('备注')
            self.操作 = data.get('操作')

    def __iter__(self) -> dict:
        yield "序号", self.序号,
        yield "考试场次", self.考试场次,
        yield "课程名称", self.课程名称,
        yield "考核方式", self.考核方式,
        yield "考试形式", self.考试形式,
        yield "考试时间", self.考试时间,
        yield "考场", self.考场,
        yield "座位号", self.座位号,
        yield "准考证号", self.准考证号,
        yield "备注", self.备注,
        yield "操作", self.操作,

    def __str__(self) -> str:
        return str(dict(self))

    def __repr__(self) -> str:
        return str(dict(self))


class Examination(Login):
    """ 考试安排爬虫 """
    __属性映射: list = [
        '序号', '考试场次', '课程名称', '考核方式', '考试形式',
        '考试时间', '考场', '座位号', '准考证号', '备注', '操作']
    考试表: list[ExamSubject] = []

    async def __accessExamHTML(self) -> str:
        """ 访问考试页面, 返回HTML """
        url = parse.urljoin(self.url, "jsxsd/xsks/xsksap_list")
        data = {'xnxqid': self.学期}
        resp = await self.client.post(url=url, headers=self.headers, data=data, cookies=self.cookies)
        return resp.text

    def __analysisHTML(self, html) -> list:
        """ 解析HTML到类属性 """
        soup = BeautifulSoup(html, 'html.parser')
        考试表 = soup.find('table', id="dataList")
        所有科目 = 考试表.find_all('tr')[1:]  # 按科目放入列表
        for 科目 in 所有科目:
            全部属性 = 科目.find_all('td')  # 当前节次的每日课表
            data = {}
            for index in range(len(全部属性)):
                data |= {self.__属性映射[index]: 全部属性[index].next_element.strip()}
            self.考试表.append(ExamSubject(data))
        return self.考试表

    async def __call__(self) -> list[ExamSubject]:
        """ 登录, 并返回考试表 """
        if await self.checkLogin() == False:
            await super().__call__()
        return self.__analysisHTML(await self.__accessExamHTML())

