# -*- coding: utf-8 -*-

import os
from sqlalchemy.ext.declarative import declarative_base
from settings import ENV

if ENV == 1:
    from settings.dev import *
elif ENV == 2:
    from settings.test import *
else:
    from settings.prod import *

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))

# 创建对象的基类:
Base = declarative_base()
