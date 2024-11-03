# -*- coding: utf-8 -*-
import pprint

# from apscheduler.schedulers.blocking import BlockingScheduler
from plugins.device_monitor import DeviceInfo
# from spider_by_openapi.cj.cj_commission_detail import oms_lingxing_api_in_stock


if __name__ == '__main__':
    # scheduler = BlockingScheduler()

    # 定时运行
    # scheduler.add_job(oms_lingxing_api_in_stock, 'cron', hour='3', minute='10')  # 云鲸-WMS US站点海外仓入库明细数据

    # try:
    #     scheduler.start()
    # except SystemExit:
    #     exit()

    pprint.pp(DeviceInfo().get_memory_info())
