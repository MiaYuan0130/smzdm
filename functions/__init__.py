# -*- coding = utf-8 -*-
# @Author : WuYiPin
# @time : 2023/11/30 : 20:55
# @file : __init__.py
# @SoftWare : PyCharm

from .spider import *
from .error import *

__all__ = []
__all__ += spider.__all__
__all__ += error.__all__
