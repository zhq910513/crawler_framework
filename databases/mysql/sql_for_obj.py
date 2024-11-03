# -*- coding: utf-8 -*-

import contextlib
import json
import re
from datetime import datetime
from typing import Dict, Any

import mysql
from six import itervalues

from databases.mysql.basedb import BaseDB, SqlError
from plugins.log import logger
from settings.base import *


class MysqlProjectDB(BaseDB):
    def __init__(self, host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PWD):
        super(MysqlProjectDB, self).__init__(host, port, database, user, passwd)

    def create_table(self, table: str, sql_list: list, comment=''):
        """
        :param table:
        :param sql_list:
        :param comment:
        :return:
        """
        if sql_list and isinstance(sql_list, list):
            _sql = ','.join(sql_list)
            sql = f'CREATE TABLE {self.escape(table)} ({_sql}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_gen_ci COMMENT="{comment}"'
            self._execute(sql)
            return
        raise SqlError(f'创建数据表失败,sql语句j:{sql_list}')

    def create_table_by_dict(self, table_name, columns_dict: Dict[str, Any]):
        """
        :param table_name:
        :param columns_dict:
        :return:
        """
        # 构建 SQL 语句
        columns_sql = ', '.join([f"`{k}` {self._infer_data_type(v)}" for k, v in columns_dict.items()])
        _sql = f"CREATE TABLE `{table_name}` ({columns_sql});"
        self._execute(_sql)
        return

    @staticmethod
    def _infer_data_type(value: Any) -> str:
        """
        推断数据类型
        @param value: 字段值
        @return: 对应的 SQL 数据类型
        """
        if isinstance(value, int):
            return 'INT'
        elif isinstance(value, float):
            return 'DECIMAL(10,2)'
        elif isinstance(value, str):
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', value):  # DateTime 格式
                return 'DATETIME'
            elif len(value) > 255:
                return 'TEXT'
            else:
                return 'VARCHAR(255)'
        elif isinstance(value, bool):
            return 'TINYINT'
        else:
            return 'TEXT'

    def select(self, table_name=None, what="*", where='', offset=0, limit=None):
        """
        查询
        @param table_name:
        @param what:
        @param where: sql完整的条件，如 id=2 and data=test
        @param offset:
        @param limit:
        @return:
        """
        table_name = self.escape(table_name)
        if isinstance(what, list) or isinstance(what, tuple) or what is None:
            what = ','.join(self.escape(f) for f in what) if what else '*'
        sql_query = "SELECT %s FROM %s" % (what, table_name)
        if where:
            sql_query += " WHERE %s" % where
        if limit:
            sql_query += " LIMIT %d, %d" % (offset, limit)
        elif offset:
            sql_query += " LIMIT %d, %d" % (offset, self.max_limit)
        return self._execute(sql_query).fetchall()

    def select_to_dic(self, table_name=None, what="*", where="", order=None, offset=0, limit=None):
        """
        查询的数据集转为dict
        @param table_name:
        @param what:
        @param where:
        @param order:
        @param offset:
        @param limit:
        @return:
        """
        table_name = self.escape(table_name)
        if isinstance(what, list) or isinstance(what, tuple) or what is None:
            what = ','.join(self.escape(f) for f in what) if what else '*'
        sql_query = "SELECT %s FROM %s" % (what, table_name)
        if where:
            sql_query += " WHERE %s" % where
        if order:
            sql_query += ' ORDER BY %s' % order
        if limit:
            sql_query += " LIMIT %d, %d" % (offset, limit)
        elif offset:
            sql_query += " LIMIT %d, %d" % (offset, self.max_limit)
        db_cur = self._execute(sql_query)
        fields = [f[0] for f in db_cur.description]
        for row in db_cur:
            yield dict(zip(fields, row))

    def replace(self, table_name, **values):
        """
        替换
        @param table_name:
        @param values: dict
        @return:
        """
        table_name = self.escape(table_name)
        if values:
            _keys = ", ".join(self.escape(k) for k in values)
            _values = ", ".join([self.placeholder, ] * len(values))
            sql_query = "REPLACE INTO %s (%s) VALUES (%s)" % (table_name, _keys, _values)
        else:
            sql_query = "REPLACE INTO %s DEFAULT VALUES" % table_name
        if values:
            db_cur = self._execute(sql_query, list(itervalues(values)))
        else:
            db_cur = self._execute(sql_query)
        return db_cur.lastrowid

    def insert(self, table_name, **values):
        """
        插入
        @param table_name:
        @param values: dict
        @return:
        """
        table_name = self.escape(table_name)
        if values:
            values.update({
                'insert_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            _keys = ", ".join((self.escape(k) for k in values))
            _values = ", ".join([self.placeholder, ] * len(values))
            sql_query = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, _keys, _values)
        else:
            sql_query = "INSERT INTO %s DEFAULT VALUES" % table_name
        try:
            if values:
                db_cur = self._execute(sql_query, list(itervalues(values)))
            else:
                db_cur = self._execute(sql_query)
            return db_cur.lastrowid
        except Exception as e:
            logger.error(f'插入数据失败：{values}，table_name:{table_name},error:{e}')

    def update(self, table_name, where="1=0", **values):
        """
        更新
        @param table_name:
        @param where: sql完整的条件，如 id=2 and data=test
        @param values: dict
        @return:
        """
        table_name = self.escape(table_name)
        with contextlib.suppress(KeyError):
            values.pop('add_time')
        values.update({
            'insert_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        _key_values = ", ".join([
            "%s = %s" % (self.escape(k), self.placeholder) for k in values
        ])
        sql_query = "UPDATE %s SET %s WHERE %s" % (table_name, _key_values, where)
        return self._execute(sql_query, list(itervalues(values)))

    def delete(self, table_name, where=""):
        """
        删除
        @param table_name:
        @param where: sql完整的条件，如 id=2 and data=test
        @return:
        """
        table_name = self.escape(table_name)
        sql_query = "DELETE FROM %s" % table_name
        if where:
            sql_query += " WHERE %s" % where
        return self._execute(sql_query)

    def add_replace(self, table_name, **values):
        """
        插入或更新，存在更新，反之插入
        @param table_name:
        @param values:
        @return:
        """
        if not values:
            return
        _table_name = self.escape(table_name)
        values.update({
            'insert_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
        _keys = ", ".join((self.escape(k) for k in values))
        _values = ", ".join([self.placeholder, ] * len(values))
        sql_query = "REPLACE INTO %s (%s) VALUES (%s)" % (table_name, _keys, _values)
        try:
            db_cur = self._execute(sql_query, list(itervalues(values)))
            return db_cur.lastrowid
        except Exception as e:
            logger.error(f'插入数据失败：{values}，table_name:{table_name},error:{e}')

    def insert_update(self, table_name, where='1=0', **values):
        """
        插入或更新，存在更新，反之插入
        @param table_name:
        @param where:
        @param values:
        @return:
        """

        query = self.select(table_name=table_name, where=where)
        if query:
            return self.update(table_name=table_name, where=where, **values)
        else:
            return self.insert(table_name=table_name, **values)

    def insert_update_with_updatetime(self, table_name, where='1=0', **values):
        query = self.select(table_name=table_name, where=where)
        if query:
            table_name = self.escape(table_name)
            with contextlib.suppress(KeyError):
                values.pop('add_time')
            values.update({
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            _key_values = ", ".join([
                "%s = %s" % (self.escape(k), self.placeholder) for k in values
            ])
            sql_query = "UPDATE %s SET %s WHERE %s" % (table_name, _key_values, where)
            return self._execute(sql_query, list(itervalues(values)))
        else:
            table_name = self.escape(table_name)
            if values:
                values.update({
                    'insert_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                _keys = ", ".join((self.escape(k) for k in values))
                _values = ", ".join([self.placeholder, ] * len(values))
                sql_query = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, _keys, _values)
            else:
                sql_query = "INSERT INTO %s DEFAULT VALUES" % table_name
            if values:
                self._execute(sql_query, list(itervalues(values)))
            else:
                self._execute(sql_query)

    def insert_pandas(self, df, table_name):
        """
        将 DataFrame 中的数据插入到 MySQL 数据库中的指定表中，并根据主键更新数据
        参数：
        - table_name: 要插入/更新数据的表名
        - df: 包含数据的 DataFrame
        - primary_key: 表的主键列名
        """
        new_list = df.fillna('')
        list_of_dicts = new_list.to_dict(orient='records')
        for data in list_of_dicts:
            _table_name = self.escape(table_name)
            _keys = ", ".join((self.escape(k) for k in data))
            _values = ", ".join([self.placeholder, ] * len(data))
            sql_query = "REPLACE INTO %s (%s) VALUES (%s)" % (table_name, _keys, _values)
            _sql_value = [None if x == "" else x for x in list(itervalues(data))]
            all_none = all(x is None for x in _sql_value)  # 过滤空行
            if not all_none:
                try:
                    self._execute(sql_query, _sql_value)
                except Exception as e:
                    logger.error(
                        f'插入数据失败：{json.dumps(data, ensure_ascii=False)}，table_name:{table_name},error:{e}')

    def delete_data_from_table(self, table_name, where=None):
        sql_query = f"""DELETE FROM {table_name}"""
        if where:
            sql_query += " WHERE %s" % where
        try:
            self._execute(sql_query)
        except mysql.connector.errors.ProgrammingError as e:
            logger.error(f'清除表数据失败，table_name:{table_name},error:{e}')
