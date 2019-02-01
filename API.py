# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------
from Core.Core import Core
from ServiceWheel.Service import Service
from OtherToolWheel.Tools import Tools

__Version__ = '0.1'
__Author__ = 'sn0wfree'
__Description__ = 'It is a extra collections of Tools, \
                    which is help to develop some functions \
                    without reproduce some existed wheel'


class API(object):
    """
    api main function
    """

    def __init__(self):

        self._Core_ = Core()
        self._Service_ = Service()
        self._Tools_ = Tools()
        pass


if __name__ == '__main__':
    pass
