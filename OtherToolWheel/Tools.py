# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------
import pandas as pd
import sqlite3


class Tools(object):

    def __init__(self):
        pass

    def LoadCacheFunctions(self, *args, **kwargs):
        import CacheFunctions
        return CacheFunctions.LastUpdatedOrderedDict

    def LoadWrappers(self):
        import Wrappers
        return Wrappers.LRUCache

    def LoadInMemoryDB(self):
        import AboutDB
        return AboutDB.inMemoryDB

    def LoadDB(self):
        import AboutDB
        return AboutDB.DBPool


if __name__ == '__main__':
    pass
