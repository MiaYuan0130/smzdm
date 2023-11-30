# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/30 : 21:42
# @file : error.py
# @SoftWare : PyCharm

__all__ = []


class BaseError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message
