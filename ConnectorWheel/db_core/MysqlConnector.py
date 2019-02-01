# coding=utf8
import pandas as pd
import pymysql
import sqlalchemy

from collections import namedtuple


class BaseMysql(object):

    def __init__(self, MysqlName,
                 host='localhost',
                 port=3306,
                 user='web',
                 passwd='Imweb',
                 charset='UTF8',
                 db='com_stable'):

        SQLConnector = namedtuple(
            MysqlName, ['host',
                        'port',
                        'user',
                        'passwd',
                        'charset',
                        'db'])
        self.para = SQLConnector(host, port, user, passwd, charset, db)

    def SelfConnect(self):
        """
        create the connector for the mysql sql command.

        :return:
        """
        conn = pymysql.connect(host=self.para.host,
                               port=self.para.port,
                               user=self.para.user,
                               passwd=self.para.passwd,
                               charset=self.para.charset,
                               db=self.para.db)
        return conn

    def SelfEngine(self):
        """
        create the cursor for the msyql sql command.
        :return:
        """
        engine_str = 'mysql+pymysql://{}:{}@{}:{}/{}?charset={}'

        # use sqlalchemy to create engine
        engine = sqlalchemy.create_engine(engine_str.format(self.para.user,
                                                            self.para.passwd,
                                                            self.para.host,
                                                            self.para.port,
                                                            self.para.db,
                                                            self.para.charset))

        return engine

    def SHOWDATABASES(self):
        """
        simple command for showing all databases。


        :return:
        """
        return self.Excutesql(sql='SHOW DATABASES')

    def SHOWTABLES(self):
        """
        simple command for  showing all tables under current datavases under given the connector parameters.
        :return:
        """
        return self.Excutesql(sql='SHOW TABLES')


class ConnectMysql(BaseMysql):

    def __init__(self, *args, **kwargs):
        """

        """
        super().__init__(*args, **kwargs)

    def sql2data(self, sql):
        """
        this is the function to get data from sql queries and
        transform the data into the dataframe via pandas
        :param sql:
        :return:
        """
        # type: (str) -> dataframe
        conn = self.SelfConnect()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    def DetectConnectStatus(self, returnresult=True, printout=False):
        """
        detect function for connect the mysql server and return useful information to response the expect messages.

        :param returnresult:
        :param printout:
        :return:
        """

        try:
            result = self.Excutesql()
            status = 'Good connection!'
            if printout:
                print(status)
        except pymysql.OperationalError as e:
            result = str(e)
            status = 'Bad connection!'
            if printout:
                print(e)
        finally:
            if returnresult:
                return result
            else:
                return status

    def Excutesql(self, sql='SHOW DATABASES'):
        """
        execute the sql command for the any reasonable sql commands and queries

        :param sql:
        :return:
        """

        conn = self.SelfConnect()
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result


if __name__ == '__main__':
    pass
