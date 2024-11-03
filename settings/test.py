# -*- coding: utf-8 -*-

CUR_HOST = 'localhost'

# MYSQL
MYSQL_HOST = 'rm-bp1j41jyg3d0zq372go.mysql.rds.aliyuncs.com'
MYSQL_USER = 'haijun'
MYSQL_PWD = 'nWbQwA5tDS'
MYSQL_PORT = 3306
MYSQL_DB = 'overseas'

# Redis 配置
REDIS_HOST = CUR_HOST
REDIS_PWD = ''
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASS = ""

# Mongo 配置
MONGODB_HOST = '27.150.182.135'
MONGODB_PORT = 27017
MONGODB_USER = 'root'
MONGODB_PWD = 'root123456'
MONGODB_DB = 'Quotation'
MONGODB_POOL_SIZE = 10
MONGODB_URL = f'mongodb://{MONGODB_HOST}'

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
chrome_log_dir = r'D:\google\googleChrome\Default'
# command = f'{chrome_path} about:blank --remote-debugging-port=9222 --user-data-dir="{log_dir}"'
chrome_command = [chrome_path, 'about:blank', '--remote-debugging-port=9300', f'--user-data-dir={chrome_log_dir}']

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
