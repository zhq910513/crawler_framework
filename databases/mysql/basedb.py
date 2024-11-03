# -*- coding: utf-8 -*-


from __future__ import unicode_literals, division, absolute_import

import mysql.connector
from retry import retry

from settings.base import *


class SqlError(Exception):
    pass


class BaseDB(object):
    placeholder = '%s'
    max_limit = -1

    def __init__(self, host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PWD):
        """
        :param host:
        :param port:
        :param database:
        :param user:
        :param passwd:
        """
        self.conn = None
        self.database_name = database
        self.conn_sql(host, port, database, user, passwd)

    @retry(tries=3)
    def conn_sql(self, host, port, database,
                 user, passwd):
        self.conn = mysql.connector.connect(user=user, password=passwd,
                                            host=host, port=port, autocommit=True)
        if database not in [x[0] for x in self._execute(sql_query='show databases')]:
            self._execute(sql_query='CREATE DATABASE %s' % self.escape(database))
        self.conn.database = database

    @staticmethod
    def escape(string):
        return '`%s`' % string

    @property
    def db_cur(self):
        """
        :return:
        """
        try:
            if self.conn.unread_result:
                self.conn.get_rows()
            return self.conn.cursor()
        except (mysql.connector.OperationalError, mysql.connector.InterfaceError):
            self.conn.ping(reconnect=True)
            self.conn.database = self.database_name
            return self.conn.cursor()

    def _execute(self, sql_query, values=None):
        """
        :param sql_query:
        :param values:
        :return:
        """
        if values is None:
            values = []
        db_cur = self.db_cur
        db_cur.execute(sql_query, values)
        return db_cur
