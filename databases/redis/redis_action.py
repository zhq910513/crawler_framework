# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import List, Optional, Any, Union

import redis
from redis import RedisError

from plugins.log import logger
from settings.base import *


class RedisOperationError(Exception):
    """Redis操作异常"""
    pass


class RedisAction(redis.Redis):
    """
    Redis操作基础类，提供常用的Redis操作方法
    """

    def __init__(
            self,
            host: str = REDIS_HOST,
            port: int = REDIS_PORT,
            password: str = REDIS_PASS,
            db: int = REDIS_DB
    ):
        """
        初始化Redis连接

        Args:
            host: Redis服务器地址
            port: Redis服务器端口
            password: Redis密码
            db: 数据库编号
        """
        super().__init__(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False  # 保持原始bytes类型
        )
        self._check_connection()

    def _check_connection(self) -> None:
        """检查Redis连接是否正常"""
        try:
            self.ping()
        except RedisError as e:
            logger.error(f"Redis连接失败: {e}")
            raise RedisOperationError(f"Redis连接失败: {e}")

    @staticmethod
    def safe_decode(value: Optional[bytes]) -> Optional[str]:
        """
        安全解码bytes为字符串

        Args:
            value: 需要解码的bytes值

        Returns:
            解码后的字符串或None
        """
        if value is None:
            return None
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"解码失败: {e}")
            return None

    def pop_list(self, key: str, size: int) -> List[str]:
        """
        从列表中弹出指定数量的值

        Args:
            key: Redis键名
            size: 需要弹出的元素数量

        Returns:
            List[str]: 弹出的值列表

        Raises:
            RedisOperationError: Redis操作异常
        """
        if not isinstance(size, int) or size <= 0:
            raise ValueError("size必须是正整数")

        try:
            vals = []
            for _ in range(size):
                value = self.lpop(key)
                if value is None:
                    break
                decoded_value = self.safe_decode(value)
                if decoded_value is not None:
                    vals.append(decoded_value)
            return vals
        except RedisError as e:
            logger.error(f"从列表弹出值失败 - key:{key}, size:{size}, error:{e}")
            raise RedisOperationError(f"Redis操作失败: {e}")
        except Exception as e:
            logger.error(f"未知错误 - key:{key}, size:{size}, error:{e}")
            raise

    def copy_all(self, source_key: str, target_key: str) -> bool:
        """
        备份Redis数据，从source_key备份到target_key

        Args:
            source_key: 源键名
            target_key: 目标键名

        Returns:
            bool: 操作是否成功

        Raises:
            RedisOperationError: Redis操作异常
        """
        try:
            # 使用管道执行操作
            with self.pipeline() as pipe:
                # 获取源数据
                vals = self.lrange(source_key, 0, -1)
                if not vals:
                    logger.warning(f"源键 {source_key} 为空")
                    return True

                # 删除目标键并复制数据
                pipe.delete(target_key)
                pipe.rpush(target_key, *vals)
                pipe.execute()

            logger.info(f"成功将 {source_key} 复制到 {target_key}")
            return True

        except RedisError as e:
            logger.error(f"复制失败 - source:{source_key}, target:{target_key}, error:{e}")
            raise RedisOperationError(f"Redis操作失败: {e}")
        except Exception as e:
            logger.error(f"未知错误 - source:{source_key}, target:{target_key}, error:{e}")
            raise

    def lpop_zset(self, key: str) -> Optional[Any]:
        """
        从有序集合中取出并删除优先级最高的元素

        Args:
            key: Redis键名

        Returns:
            Optional[Any]: 解析后的JSON数据或None

        Raises:
            RedisOperationError: Redis操作异常
        """
        try:
            with self.pipeline() as pipe:
                pipe.multi()
                pipe.zrange(key, 0, 0)
                pipe.zremrangebyrank(key, 0, 0)
                results, count = pipe.execute()

                if results and results[0]:
                    try:
                        return json.loads(self.safe_decode(results[0]))
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败 - key:{key}, value:{results[0]}, error:{e}")
                        return None
                return None

        except RedisError as e:
            logger.error(f"从有序集合取值失败 - key:{key}, error:{e}")
            raise RedisOperationError(f"Redis操作失败: {e}")
        except Exception as e:
            logger.error(f"未知错误 - key:{key}, error:{e}")
            raise

    def push_list(self, key: str, value: Union[str, dict, list]) -> bool:
        """
        向列表推入数据

        Args:
            key: Redis键名
            value: 要推入的值

        Returns:
            bool: 操作是否成功
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            self.rpush(key, value)
            return True
        except Exception as e:
            logger.error(f"推入数据失败 - key:{key}, value:{value}, error:{e}")
            return False

    def get_list_length(self, key: str) -> int:
        """
        获取列表长度

        Args:
            key: Redis键名

        Returns:
            int: 列表长度
        """
        try:
            return self.llen(key)
        except Exception as e:
            logger.error(f"获取列表长度失败 - key:{key}, error:{e}")
            return 0

    def clear_key(self, key: str) -> bool:
        """
        清除指定键的数据

        Args:
            key: Redis键名

        Returns:
            bool: 操作是否成功
        """
        try:
            self.delete(key)
            return True
        except Exception as e:
            logger.error(f"清除键失败 - key:{key}, error:{e}")
            return False

    def backup_key(self, key: str) -> bool:
        """
        备份指定键的数据（添加时间戳后缀）

        Args:
            key: Redis键名

        Returns:
            bool: 操作是否成功
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_key = f"{key}_backup_{timestamp}"
        try:
            return self.copy_all(key, backup_key)
        except Exception as e:
            logger.error(f"备份失败 - key:{key}, error:{e}")
            return False
