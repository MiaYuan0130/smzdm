# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/22 : 19:44
# @file : encrypt.py
# @SoftWare : PyCharm
import time
import ctypes
import hashlib


class Encrypt:
    @staticmethod
    def get_update_param(param, method="GET"):
        base_dict = {
            "f": "android",
            "v": "10.6.10",
            "weixin": "1",
            "time": f"{int(time.time() * 1000)}",
            # "time": "1700798111000",
            "basic_v": "0"
        }
        if method == "GET":
            base_dict.update({"sign": Encrypt._encrypt(base_dict, param)})
        elif method == "POST":
            base_dict.update({"sign": Encrypt._encrypt(base_dict, param)})
        return base_dict

    @staticmethod
    def _encrypt(base_dict, param):
        base_dict.update(param)
        string = '&'.join([k + '=' + str(v) for (k, v) in sorted(base_dict.items()) if v != ""])
        string = string + "&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC"
        return Encrypt._md5(string.replace(' ', '')).upper()

    @staticmethod
    def _md5(string: str):
        # apr1$AwP!wRRT$gJ/q.X24poeBInlUJC
        arr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        string_md5 = hashlib.md5(string.encode()).digest()
        return_string = ''
        for b in string_md5:
            return_string = return_string + arr[Encrypt.unsigned_right_shitf(b, 4) & 15] + arr[b & 15]
        return return_string.lower()

    @staticmethod
    def int_overflow(val):
        maxint = 2147483647
        if not -maxint - 1 <= val <= maxint:
            val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
        return val

    @staticmethod
    def unsigned_right_shitf(n, i):
        # 数字小于0，则转为32位无符号uint
        if n < 0:
            n = ctypes.c_uint32(n).value
        # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
        if i < 0:
            return -Encrypt.int_overflow(n << abs(i))
        # print(n)
        return Encrypt.int_overflow(n >> i)


if __name__ == "__main__":
    appen_dic = {
        "token": "BB-1RsKxXyCRAX0UCUtN9SG9anGXn5cA8NFJ2Ke0lxxDXSs5mylF7g5XaXeDmdR3Zo9iU2A2JGgKFXWYSXOxis9p775EKs%3D",
        "offset": 0,
        "get_total": 1,
        "target_smzdm_id": "2587985363",
        "limit": 20
    }
    print(Encrypt.get_update_param(appen_dic))
