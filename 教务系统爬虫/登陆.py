from Crypto.Cipher import AES
from urllib import parse
from . import 验证码识别
from typing import Union
import asyncio
import base64
import httpx


class Encrypt(object):
    def encrypt(self, text: str) -> str:
        """ 加密 """
        cipher = AES.new("yangrucheng".rjust(32, "6").encode(), AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(text.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

    def decrypt(self, ciphertext: str) -> str:
        """ 解密 """
        ciphertext = base64.b64decode(ciphertext.encode())
        nonce, tag, ciphertext = \
            ciphertext[:16], ciphertext[16:32], ciphertext[32:]
        cipher = AES.new("yangrucheng".rjust(
            32, "6").encode(), AES.MODE_EAX, nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()


class Login(Encrypt):
    """
        # 登陆基类
        `username: str = None` 用户名, 通常是学号 
        `password: str = None` 密码 
        `token: str = None` 加密凭证, 用于短时间内第二次创建对象 
        `term: str = "2022-2023-1"` 学期 
        `url: str = "http://jwxt.xtu.edu.cn"`教务系统URL 
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Origin": "http://jwxt.xtu.edu.cn"}
    url: str
    学期: str
    timeout = 3
    max_retry = 3
    cookies = None

    def __init__(
        self,
        username: Union[str, int] = None,
        password: str = None,
        token: str = None,
        term: str = "2022-2023-1",
        url: str = "http://jwxt.xtu.edu.cn"
    ) -> None:
        # 构造对象时不执行登陆
        self.client = httpx.AsyncClient(http2=True, timeout=self.timeout)
        self.username = username
        self.password = password
        self.学期 = term if term else "2022-2023-1"
        self.url = url if url else "http://jwxt.xtu.edu.cn"
        if token:
            self.cookies = eval(self.decrypt(token))

    async def __call__(self) -> str:
        """ 登陆并返回token凭证 """
        if await self.checkLogin():
            return self.encrypt(str(dict(self.cookies)))
        else:
            await self.__accessHome()
            await self.__getCode()
            await self.__getEncode()
            await self.__postLogin()
            return await self.__call__()

    async def __accessHome(self, retry=0):
        """ 访问登录页 """
        url = parse.urljoin(self.url, "jsxsd")
        try:
            resp = await self.client.get(url=url, headers=self.headers, cookies=self.cookies)
        except (BaseException, Exception) as e:
            if retry < self.max_retry:
                return await self.__accessHome(retry+1)
            else:
                raise e
        else:
            self.cookies = resp.cookies
            return resp

    async def __postLogin(self, retry=0):
        """ 发送登录请求 """
        url = parse.urljoin(self.url, "jsxsd/xk/LoginToXk")
        data = {
            'USERNAME': self.username,
            'PASSWORD': self.password,
            'encoded': self.encode,
            'RANDOMCODE': self.code
        }
        try:
            resp = await self.client.post(url=url, data=data, headers=self.headers, cookies=self.cookies)
        except (BaseException, Exception) as e:
            if retry < self.max_retry:
                return await self.__postLogin(retry+1)
            else:
                raise e
        else:
            self.cookies = resp.cookies
            return resp

    async def __getCode(self, retry=0) -> str:
        """ 获取图形验证码结果 """
        url = parse.urljoin(self.url, "jsxsd/verifycode.servlet")
        try:
            resp = await self.client.get(url=url, headers=self.headers, cookies=self.cookies)
            code = 验证码识别.main(resp.content)
        except (BaseException, Exception) as e:
            if retry < self.max_retry:
                return await self.__getCode(retry+1)
            else:
                raise e
        else:
            self.code = code
            self.cookies = resp.cookies
            return code

    async def __getEncode(self, retry=0) -> str:
        """ 获取加密后的encode """
        url = parse.urljoin(self.url, "jsxsd/xk/LoginToXk?flag=sess")
        try:
            resp = await self.client.post(url=url, headers=self.headers, cookies=self.cookies)
            assert resp.status_code == 200
            data: str = resp.json()['data']
            scode = data.split('#')[0]
            sxh = data.split('#')[1]
            code = f"{self.username}%%%{self.password}"
            i = 0
            encode = ""
            while i < len(code):
                if i < 20:
                    encode = encode + code[i:i+1] + scode[0:int(sxh[i:i+1])]
                    scode = scode[int(sxh[i:i+1]):len(scode)]
                else:
                    encode = encode + code[i:len(code)]
                    i = len(code)
                i += 1
        except (BaseException, Exception) as e:
            if retry < self.max_retry:
                return await self.__getCode(retry+1)
            else:
                raise e
        else:
            self.encode = encode
            self.cookies = resp.cookies
            return encode

    async def checkLogin(self, token: str = None) -> bool:
        """ 检查登陆是否成功, 支持判断传入的token是否未过期 """
        if token:
            self.cookies = dict(self.decrypt(token))
        url = parse.urljoin(self.url, "jsxsd/framework/xsMain.jsp")
        try:
            resp = await self.client.get(url=url, headers=self.headers, cookies=self.cookies)
            assert resp.status_code == 200
        except:
            return False
        else:
            return True

