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
    login = Login("2021********", "******", term="2022-2023-1")

    login.__class__ = Scheme  # 类似C语言的强制类型转换
    dataList: list[Subject] = await login()  # 培养方案列表
    for value in dataList:
        print(dict(value))

    login.__class__ = EmptyClassroom
    dataList: list[Classroom] = await login()
    for value in dataList:
        print(dict(value))

if __name__ == "__main__":
    asyncio.run(demo())
