# -*- coding:utf-8 -*-
from collections import OrderedDict


class LastUpdatedOrderedDict(OrderedDict):

    def __init__(self, capacity):
        super(LastUpdatedOrderedDict, self).__init__()
        self._capacity = capacity

    def __setitem__(self, key, value):
        containsKey = 1 if key in self else 0
        if len(self) - containsKey >= self._capacity:
            last = self.popitem(last=False)
            # print 'remove:', last
        if containsKey:
            del self[key]
            # print 'set:', (key, value)
        else:
            pass
            # print 'add:', (key, value)
        OrderedDict.__setitem__(self, key, value)


def Lcache(capacity=250):
    memo = LastUpdatedOrderedDict(capacity)

    def cache(func):
        def _wrapper(*args):
            res = memo.get(args, None)
            if res is not None:
                return res
            else:
                res = func(*args)
                memo[args] = res
            return res
        return _wrapper
    return cache


if __name__ == '__main__':
    pass
