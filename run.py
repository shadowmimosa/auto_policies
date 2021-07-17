#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File     :   run.py
@Time     :   2020/08/13 13:11:01
@Author   :   ShadowMimosa
@Version  :   1.0
@Contact  :   shadowmimosa@163.com
@Copyright:   Copyright (c) 2020 by ShadowMimosa, shadowmimosa@163.com
@License  :   MIT License
@Desc     :   None
'''

# here put the import lib
import threading
from loguru import logger
from functools import wraps

DEBUG = False


@logger.catch(reraise=True)
def reraise(func, *args, **kwargs):
    return func(*args, **kwargs)


@logger.catch()
def unraise(func, *args, **kwargs):
    return func(*args, **kwargs)


class RunFunc(threading.local):
    def __init__(self, target='', default=None, raise_err=False):
        self.target = target
        self.default = default
        if raise_err is None and DEBUG:
            raise_err = True
        self.raise_err = raise_err

        super().__init__()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.raise_err:
                return self.reraise(func, *args, **kwargs)
            else:
                return self.unraise(func, *args, **kwargs)

        return wrapper

    @logger.catch(reraise=True)
    def reraise(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    @logger.catch()
    def unraise(self, func, *args, **kwargs):
        return func(*args, **kwargs)


def run_func(target='', default=None, raise_err=None):
    if raise_err is None and DEBUG:
        raise_err = True

    def decorator(func):
        def wrapper(*args, **kwargs):
            if raise_err:
                result = reraise(func, *args, **kwargs)
            else:
                result = unraise(func, *args, **kwargs)

            if result is None:
                return default

            return result

        return wrapper

    return decorator
