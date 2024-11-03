# -*- coding: utf-8 -*-

CUR_HOST = '127.0.0.1'

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

# CHROME
CHROME_DRIVER_PATH = r'/opt/chrome/google-chrome'
CHROME_PROFILE_PATH = r'/opt/chrome'

chrome_path = '/opt/google/chrome/google-chrome'
chrome_log_dir = '/data/google/google-chrome/Default'
chrome_command = [chrome_path, '--no-sandbox', 'about:blank', '--remote-debugging-port=9300',
                  f'--user-data-dir={chrome_log_dir}']

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
