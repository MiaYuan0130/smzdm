# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/26 : 23:04
# @file : test.py
# @SoftWare : PyCharm
from functions.spider import UserIdSpiderAPP


def ab():
    yield []


user_fans_or_followers = ab()
print(user_fans_or_followers)
spider = UserIdSpiderAPP(is_first=False, logger_name='console_logger')
result = spider._crawl_fans_or_follower_helper(user_fans_or_followers)
print(result)
