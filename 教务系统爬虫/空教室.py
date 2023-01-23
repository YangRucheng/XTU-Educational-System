from bs4 import BeautifulSoup
from urllib import parse
from .登陆 import Login
import asyncio


class Classroom(object):
    """" 单个教室的空闲情况 """
    教室: str = ""
    空闲情况: list[str]
    文本: str = ""

    def __init__(self, classroom: str = "") -> None:
        self.教室 = classroom
        self.文本 = ""
        self.空闲情况 = []

    def __getText(self) -> str:
        """ 将空闲情况整理成文本 """
        if "空" not in self.空闲情况:
            self.文本 = "全天满"
        elif "满" not in self.空闲情况:
            self.文本 = "全天空闲"
        elif "满" not in self.空闲情况[0:4]:
            self.文本 = "白天空闲"
        else:
            if "满" not in self.空闲情况[0:2]:
                self.文本 += "上午 "
            else:
                for index in range(0, 2):
                    if self.空闲情况[index] == "空":
                        self.文本 += f"{index*2+1}-{index*2+2}节 "
            if "满" not in self.空闲情况[2:4]:
                self.文本 += "下午 "
            else:
                for index in range(2, 4):
                    if self.空闲情况[index] == "空":
                        self.文本 += f"{index*2+1}-{index*2+2}节 "
            if "满" not in self.空闲情况[4:5]:
                self.文本 += "晚上 "
            self.文本 += "空闲" if len(self.文本) else ""

    def __iter__(self) -> dict:
        self.__getText()
        yield "教室", self.教室,
        yield "文本", self.文本,
        yield "空闲情况", self.空闲情况,

    def __str__(self) -> str:
        return str(dict(self))

    def __repr__(self) -> str:
        return str(dict(self))


class EmptyClassroom(Login):
    """ 空闲教室爬虫 """
    空闲课表: list[Classroom] = []
    空闲课表JSON: list[dict] = []

    async def __accessEmptyHTML(self) -> str:
        """ 访问空教室页面, 返回HTML """
        url = parse.urljoin(self.url, "jsxsd/kbxx/kxjs_query")
        data = {'xzlx': 0}  # 今天为0, 明天为1
        resp = await self.client.post(url=url, headers=self.headers, data=data, cookies=self.cookies)
        return resp.text

    def __analysisHTML(self, html) -> list:
        """ 解析HTML """
        soup = BeautifulSoup(html, 'html.parser')
        空教室表 = soup.find('table', id="dataList")
        所有教室 = 空教室表.find_all('tr')[2:]  # 按教室放入列表
        for 教室 in 所有教室:
            属性 = 教室.find_all('td')  # 当前节次的每日课表
            classroom = Classroom(属性[0].next_element.strip())
            for 情况 in 属性[1:6]:
                classroom.空闲情况.append(情况.find('font').next_element.strip())
            self.空闲课表.append(classroom)
            self.空闲课表JSON.append(
                {"教室": classroom.教室, "空闲情况": classroom.空闲情况, "文本": classroom.文本})
        return self.空闲课表

    async def __call__(self) -> list[Classroom]:
        """ 登陆, 并返回空闲课表 """
        if await self.checkLogin() == False:
            await super().__call__()
        return self.__analysisHTML(await self.__accessEmptyHTML())


