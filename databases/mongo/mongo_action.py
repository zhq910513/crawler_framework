# -*- coding: utf-8 -*-

from pymongo import MongoClient, UpdateOne, InsertOne

from plugins.log import logger
from settings.base import *


class MongoDBHelper(object):
    """
    MongoDB数据库操作简化类
    """

    def __init__(self, host=MONGODB_HOST, port=MONGODB_PORT, username=MONGODB_USER, password=MONGODB_PWD, database=MONGODB_DB):
        """
        初始化MongoDB连接
        """
        self.client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password
        )
        self.db = self.client[database]

    def get_collection(self, collection_name):
        """
        获取指定集合
        """
        return self.db[collection_name]

    def insert_or_update(self, collection_name, unique_key, data):
        """
        插入或更新数据
        :param collection_name: 集合名称
        :param data: 要插入/更新的数据(字典格式)
        :param unique_key: 用于判断是否存在的唯一键
        :return: 操作结果
        """
        try:
            collection = self.get_collection(collection_name)

            # 如果数据是列表，则为批量操作
            if isinstance(data, list):
                result = self._batch_insert_or_update(collection, data, unique_key)
            else:
                result = self._single_insert_or_update(collection, data, unique_key)

            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"操作失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _single_insert_or_update(collection, data, unique_key):
        """
        单条数据插入或更新
        """
        if unique_key in data:
            query = {unique_key: data[unique_key]}
            return collection.update_one(
                query,
                {'$set': data},
                upsert=True
            )
        else:
            return collection.insert_one(data)

    @staticmethod
    def _batch_insert_or_update(collection, data_list, unique_key):
        """
        批量数据插入或更新
        """
        operations = []
        for data in data_list:
            if unique_key in data:
                operations.append(
                    UpdateOne(
                        {unique_key: data[unique_key]},
                        {'$set': data},
                        upsert=True
                    )
                )
            else:
                operations.append(InsertOne(data))

        if operations:
            return collection.bulk_write(operations)
        return None

    def find_one(self, collection_name, query=None):
        """
        查询单条数据
        :param collection_name: 集合名称
        :param query: 查询条件
        :return: 查询结果
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query or {})
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def find_many(self, collection_name, query=None, limit=0):
        """
        查询多条数据
        :param collection_name: 集合名称
        :param query: 查询条件
        :param limit: 限制返回数量
        :return: 查询结果
        """
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query or {})
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def delete_one(self, collection_name, query):
        """
        删除单条数据
        :param collection_name: 集合名称
        :param query: 删除条件
        :return: 删除结果
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"删除失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def close(self):
        """
        关闭数据库连接
        """
        self.client.close()
