# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/24 : 11:47
# @file : constants.py
# @SoftWare : PyCharm
import json
import os


__all__ = ['Constants']
filepath = os.path.dirname(os.path.realpath(__file__))


class Constants:
    # MAX_WORKERS = 10
    # BACKUP_COUNT = 10
    # CATEGORY = [("笔记", 172), ("好文", 174), ("众测", 176), ("数码", 177), ("汽车", 178), ("装修", 181), ("日百", 184),
    #             ("家电", 186), ("健康", 190), ("金融", 189), ("时尚", 188), ("美食", 187), ("运动", 183), ("旅行", 185),
    #             ("生活", 191), ("文娱", 180), ("亲子", 182), ("海淘", 179)]
    # URLS = {
    #     "user_info": "https://user-api.smzdm.com/users/info",
    #     "user_fans": "https://user-api.smzdm.com/friendships/his_fans",
    #     "user_followers": "https://user-api.smzdm.com/friendships/his_followers",
    #     "community": "https://article-api.smzdm.com/shequ/index"
    # }
    # MONGO_URL = "mongodb://wyp:wyp0413@121.43.171.145:27017/"
    # DB_NAME = 'smzdm'
    # with open(filepath + "/resource/params_bases.json") as f:
    #     PARAMS_BASES = json.load(f)
    # with open(filepath + "/resource/cookies_info.json") as f:
    #     COOKIE_INFO = json.load(f)
    with open(filepath + "/resource/configs.json", encoding='utf-8') as f:
        CONFIGS = json.load(f)
    DISALLOW_TO_CONFIGURE = CONFIGS.get("DISALLOW_TO_CONFIGURE")
    if os.path.exists(os.getcwd()+"/config.json"):
        with open(os.getcwd()+"/config.json") as f:
            ALLOW_TO_CONFIGURE = json.load(f)
    else:
        ALLOW_TO_CONFIGURE = CONFIGS.get("ALLOW_TO_CONFIGURE")
        with open(os.getcwd() + "/config.json", mode='w') as f:
            json.dump(ALLOW_TO_CONFIGURE, f)

    MAX_WORKERS = ALLOW_TO_CONFIGURE.get("MAX_WORKERS")
    CATEGORY = DISALLOW_TO_CONFIGURE.get("CATEGORY")
    URLS = DISALLOW_TO_CONFIGURE.get("URLS")
    MONGO_URL = ALLOW_TO_CONFIGURE.get("MONGO_URL")
    DB_NAME = ALLOW_TO_CONFIGURE.get("DB_NAME")
    PARAMS_BASES = ALLOW_TO_CONFIGURE.get("PARAMS_BASES")
    COOKIE_INFO = ALLOW_TO_CONFIGURE.get("COOKIE_INFO")
    LOG_CONFIG = ALLOW_TO_CONFIGURE.get("LOG_CONFIG")





