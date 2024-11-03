# -*- coding: utf-8 -*-


import logging
import os
import sys
from logging import handlers

from settings.base import BASE_DIR

logger = logging.getLogger(__name__)


def _logger():
    logger.setLevel(logging.DEBUG)
    logs_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    program = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    fmt_str = '%(asctime)s | %(levelname)s | %(pathname)s | %(lineno)s | %(message)s'
    formatter = logging.Formatter(fmt_str)

    _file_info = os.path.join(logs_dir, f"{program}_info.log")
    fh = handlers.RotatingFileHandler(_file_info, maxBytes=1024 ** 50, backupCount=5,
                                      encoding="utf-8", mode="a")
    fh.setLevel(logging.INFO)

    fh.setFormatter(formatter)
    logger.addHandler(fh)

    _file_error = os.path.join(logs_dir, f"{program}_error.log")
    fh1 = handlers.RotatingFileHandler(_file_error, maxBytes=1024 ** 10, backupCount=5,
                                       encoding="utf-8", mode="a")
    fh1.setLevel(logging.ERROR)
    fh1.setFormatter(formatter)
    logger.addHandler(fh1)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


_logger()
