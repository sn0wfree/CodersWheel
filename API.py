# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------


__Version__ = '0.1'
__Author__ = 'sn0wfree'
__Description__ = 'It is a extra collections of Tools, \
                    which is help to develop some functions \
                    without reproduce some existed wheel'


class API(object):

    def __init__(self):
        from Core.Core import Core
        from Service.Service import Service
        from Tools.Tools import Tools
        self._Core_ = Core()
        self._Service_ = Service()
        self._Tools_ = Tools()
        pass


if __name__ == '__main__':
    pass
