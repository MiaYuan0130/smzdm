# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/21 : 22:26
# @file : main.py
# @SoftWare : PyCharm
import time

from functions.spider import UserIdSpiderAPP

spider = UserIdSpiderAPP(is_first=False, logger_name='Spider')
spider.crawl()

