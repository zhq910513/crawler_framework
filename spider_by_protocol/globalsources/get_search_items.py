# -*- coding: utf-8 -*-
import random
import time

from plugins.log import logger
from spider_by_protocol.globalsources.base import GlobalSourceBase


class SearchItems(GlobalSourceBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gs_product_list_table = "gs_product_list"
        self.gs_supplier_list_table = "gs_supplier_list"


    def search_product_api(self, keyword, page=1):
        api = "https://www.globalsources.com/api/agg-search/DESKTOP/v3/product/search"
        json_data = {
            'pageNum': page,
            'pageSize': 80,
            'query': keyword,
            'popupFlag': False,
        }

        response = self.get_response(url=api, json_data=json_data)
        if self.parse_items(page, response.json()):
            time.sleep(random.randint(1, 5))
            return self.search_product_api(keyword=keyword, page=page + 1)

    def parse_items(self, page, json_data):
        if not json_data:
            raise ValueError

        data = json_data.get("data")
        if data:
            totalPage = data.get("totalPage", 0)
            item_list = data.get("list")
            logger.info(f"正在抓取第{page}页 当前页{len(item_list)}条 共{totalPage}页")
            if item_list and isinstance(item_list, list):
                for item in item_list:
                    supplier_id = None
                    supplier = item.get("supplier")
                    if supplier:
                        supplier_id = supplier.get("id")

                    insert_data = {
                        "product_id": item["id"],
                        "publish_date": item["firstOnlineDate"],
                        "new_product_flag": item["newProductFlag"],
                        "o2o_flag": item["o2oFlag"],
                        "company_name": item["companyName"],
                        "detail_url": item["desktopProductDetailUrl"],
                        "region": item["fobPort"],
                        "image_url": item["imageUrls"],
                        "lead_time": item["leadTime"],
                        "price": item["price"],
                        "unit": item["priceUnit"],
                        "min_order": item["minOrder"],
                        "model_number": item["modelNumber"],
                        "title": item["productName"].replace("<strong>", "").replace("</strong>", "")

                    }
                    if supplier_id:
                        insert_data["supplier_id"] = supplier_id
                        self.db.insert_or_update(self.gs_supplier_list_table, "id", supplier)

                    self.db.insert_or_update(self.gs_product_list_table, "product_id", insert_data)

            if page < totalPage:
                return True


if __name__ == '__main__':
    si = SearchItems()
    for key in [
        "phone case for iphone",

    ]:
        si.search_product_api(keyword=key)
