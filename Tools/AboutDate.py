# -*- coding:utf-8 -*-
import datetime
import calendar
import time
import pandas as pd


class HandleDate(object):
    """
    This class provides the date relative the api service and handle some date
    format.
    """

    def __init__(self):
        pass

    def GetNextQuarterByYearMonth(self, YearMonth):
        """ YearMonth = '1802'"""
        M = YearMonth[2:]
        Y = YearMonth[:2]
        if '06' > M >= '03':
            return (Y + '06', Y + '09')
        elif '09' > M >= '06':
            return (Y + '09', Y + '12')
        elif '12' > M >= '09':
            return ('%d12' % (int(Y)), '%d03' % (int(Y) + 1))
        elif M <= '12' and M < '03':
            return ('%d03' % (int(Y) + 1), '%d09' % (int(Y) + 1))

    def GetNextQuarterByQuarterNum(self, q):
        q = int(q)
        if 1 <= q < 4:
            return q + 1
        elif q == 4:
            return 1
        else:
            raise ValueError('Unknown Quarter with str format : %s ' % str(q))

    def GetCurrentQuarter(self, date=datetime.datetime.now()):

        return self.getBetweenQuarter(datetime.datetime.strftime(date, "%Y-%m-%d"))[0]

    def GetLastMonthinQuarter(self, q):
        if isinstance(q, str):
            return str(int(q) * 3)
        elif isinstance(q, (int, float)):
            return q * 3
        else:
            raise ValueError(
                'Unknown Quarter with Wrong format: {},Type: {} '.format(q, type(q)))

    def getBetweenQuarter(self, begin_date):
        quarter_list = []
        month_list = self.getBetweenMonth(begin_date)
        for value in month_list:
            tempvalue = value.split("-")
            if tempvalue[1] in ['01', '02', '03']:
                quarter_list.append("1")
            elif tempvalue[1] in ['04', '05', '06']:
                quarter_list.append("2")
            elif tempvalue[1] in ['07', '08', '09']:
                quarter_list.append("3")
            elif tempvalue[1] in ['10', '11', '12']:
                quarter_list.append("4")
        quarter_set = set(quarter_list)
        quarter_list = list(quarter_set)
        quarter_list.sort()
        return quarter_list

    def getBetweenMonth(self, begin_date):
        date_list = []
        begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(time.strftime(
            '%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m")
            date_list.append(date_str)
            begin_date = self.add_months(begin_date, 1)
        return date_list

    def add_months(self, datetimes, month):
        # auto calculate add month of datetime
        # z + pd.tseries.offsets.DateOffset(months=4, days=5)

        return datetimes + pd.tseries.offsets.DateOffset(months=month)

    def Month2StrMonthWithAutoFillup(self, Month, count=0):
        if isinstance(Month, str):
            if len(Month) == 2:
                return Month
            elif len(Month) == 1:
                return '0{}'.format(Month)
            else:
                raise ValueError('Unknown Month: {}'.format(Month))
        elif isinstance(Month, (int, float)):
            if count <= 5:
                count += 1
                return self.Month2StrMonthWithAutoFillup(str(int(Month)), count)
            else:
                raise ValueError(
                    'Unknown Situation with Int/float type Month: {}'.format(Month))
            # transform the datetime into YM format data

        else:
            raise ValueError('Unknown Month format: %s' % str(Month))


if __name__ == '__main__':
    pass
