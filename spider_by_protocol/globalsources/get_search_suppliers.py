# -*- coding: utf-8 -*-
import copy
import random
import time

from plugins.log import logger
from spider_by_protocol.globalsources.base import GlobalSourceBase
from pydantic.alias_generators import to_snake


class SearchSuppliers(GlobalSourceBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gs_supplier_list_table = "gs_supplier_list"

    def search_supplier_api(self, keyword, page=1):
        api = "https://www.globalsources.com/api/agg-search/DESKTOP/v3/supplier/search"
        json_data = {
            'pageNum': page,
            'pageSize': 80,
            'query': keyword
        }

        response = self.get_response(url=api, json_data=json_data)
        if self.parse_suppliers(page, response.json()):
            time.sleep(random.randint(1, 5))
            return self.search_supplier_api(keyword=keyword, page=page + 1)

    def parse_suppliers(self, page, json_data):
        if not json_data:
            raise ValueError

        data = json_data.get("data")
        if data:
            totalPage = data.get("totalPage", 0)
            item_list = data.get("list")
            logger.info(f"正在抓取 supplier 第{page}页 当前页{len(item_list)}条 共{totalPage}页")
            if item_list and isinstance(item_list, list):
                for item in item_list:
                    insert_data = copy.deepcopy(self.supplier_feilds())
                    supplier = item.get("supplier")
                    if supplier:
                        for key, value in supplier.items():
                            key = to_snake(key)
                            if key in ["org_id"]:
                                key = "id"
                            if key in insert_data.keys():
                                insert_data[key] = value
                    print(insert_data)
                    self.db.insert_or_update(self.gs_supplier_list_table, "id", insert_data)

            if page < totalPage:
                return True


if __name__ == '__main__':
    si = SearchSuppliers()
    for key in [
        "phone case for iphone",

    ]:
        si.search_supplier_api(keyword=key)
