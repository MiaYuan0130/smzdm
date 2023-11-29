# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/24 : 11:47
# @file : constants.py
# @SoftWare : PyCharm
import json
import os

filepath = os.path.dirname(os.path.realpath(__file__))


class Constants:
    MAX_WORKERS = 10
    BACKUP_COUNT = 10
    CATEGORY = [("笔记", 172), ("好文", 174), ("众测", 176), ("数码", 177), ("汽车", 178), ("装修", 181), ("日百", 184),
                ("家电", 186), ("健康", 190), ("金融", 189), ("时尚", 188), ("美食", 187), ("运动", 183), ("旅行", 185),
                ("生活", 191), ("文娱", 180), ("亲子", 182), ("海淘", 179)]
    URLS = {
        "user_info": "https://user-api.smzdm.com/users/info",
        "user_fans": "https://user-api.smzdm.com/friendships/his_fans",
        "user_followers": "https://user-api.smzdm.com/friendships/his_followers",
        "community": "https://article-api.smzdm.com/shequ/index"
    }
    MONGO_URL = "mongodb://localhost:27017/"
    DB_NAME = 'smzdm'
    with open(filepath + "/resource/params_bases.json") as f:
        PARAMS_BASES = json.load(f)
    with open(filepath + "/resource/cookies_info.json") as f:
        COOKIE_INFO = json.load(f)
