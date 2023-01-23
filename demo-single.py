import asyncio
from 教务系统爬虫 import (
    Login,
    Scheme, Subject,
    CourseTable, Course,
    Examination, ExamSubject,
    EmptyClassroom, Classroom
)


async def demo():
    """ 示例-培养方案 """
    scheme = Scheme("2021********", "******", term="2022-2023-1")
    dataList: list[Subject] = await scheme()  # 培养方案列表
    for value in dataList:
        print(dict(value))


async def demo():
    """ 示例-空教室 """
    empty = EmptyClassroom("2021********", "******", term="2022-2023-1")
    dataList: list[Classroom] = await empty()

if __name__ == "__main__":
    asyncio.run(demo())
