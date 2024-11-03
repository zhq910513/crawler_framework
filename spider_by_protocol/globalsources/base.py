# -*- coding: utf-8 -*-
import requests
from retry import retry

from databases.mongo.mongo_action import MongoDBHelper
from plugins.log import logger


class GlobalSourceBase(object):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.db = MongoDBHelper()

    @staticmethod
    def generate_cookies():
        return {
            'visid_incap_2720266': 'FFD5otJWSrKz5wawxmoLfoGMIWcAAAAAQUIPAAAAAAApGTYc0f3baOiaHdDxd4ce',
            'incap_ses_1565_2720266': 'iXueHAjiDAu96uaOYf+3FYGMIWcAAAAABh0AHNU0KG9irbFi3S4+jA==',
            'reese84': '3:GrBlPLF89/CsUqJgGN/9XQ==:Oo2jR6nfkXVLDj3QV8MOkSfhlDk4YD/u4mFkcWyl3YmzGugpE/926rL+hf2oEpfvWYDj3P52m8MnbuzqhrNTGlGWbpYwjxgAVOk+4QjU24EduFQo8X40r+pnoIibooRi7uHJ8T+ehV80knRhUpJI3RsOfXrW9DtyfABkb2UFDz1PK3sxoZa0Ih8oS08cdxf80wmjdBCqjPzFt9kyGlVQvSn7+YEzUvOIDIXZl92DsWo+nIDfaIhyGvsey03p+J0XvTpTbFEEg74RV75WVY8oofX9c2GzlkHZvSjt/3PnSzZ0s5Fo5wOmPZ9is/gyFXT5xShtlMVCWuhBxaIFN2qzwL2lFrVb9lPutjfRMn/O3LKuRoInaAavl0/GuJpft20oWAr1xeF9KhxQUnrFfuuNbMp6dvCs7hGwnVab+6R5/XFBej81jeGYROLRzu59QFkH+l0ZD5cJ2FBfdibf75ooa1S4o1dcDWPE9hoHRNNnwEA=:7Zve2kIQBp2lQAk/I2/9JZcXT7K/1YQmuzLuBQb4NpY=',
            'lang': 'enus',
            'bucket': 'a',
            'nlbi_2720266': 'kTU+cNRgZAU0LxSEWlZLAwAAAAABZPe1fOMl1+vxfH5tFOik',
            '_gcl_au': '1.1.528652569.1730251909',
            '_ga': 'GA1.1.1195019572.1730251911',
            'sajssdk_2015_cross_new_user': '1',
            'sensorsdata2015jssdkchannel': '%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D',
            'nlbi_2720266_2147483392': 'HSiLK0dONAbsv47mWlZLAwAAAABdwNDJ2+HBXXzom1AEoH1u',
            'visid_incap_2815037': 'j1zBIqy0RPuO+RU5Opd1oGSMIWcAAAAAQUIPAAAAAABge884mXA7tiW07ulXHBns',
            'nlbi_2815037': 'er9IFUQTmBSwXOWoQ07hiwAAAABhtAnJB/hox/n2q9623esb',
            'incap_ses_1855_2815037': 'C6hOGdtGYxuzEIzvwEi+GYyMIWcAAAAAOLZZXddJlXl+XLsEUP1toQ==',
            '_fbp': 'fb.1.1730251912087.683349651611171710',
            'nlbi_2920482': 'rT8qaKdPQ2u+kuN/ANt64gAAAAAslRKPwsfBLBmOg9Doa6l5',
            'visid_incap_2920482': 'g8gWfFGcQU6ryhDNt8aUu42MIWcAAAAAQUIPAAAAAACIz71gB9KcUKeF+ePjTh8Y',
            'incap_ses_1565_2920482': 'ikPdUdlenCPl8+aOYf+3FY2MIWcAAAAAcdLLbaxkzqApobg7ngLkQw==',
            'ul_cookie': 'y2tgfQGjQwD3MnaJBmBNUA%3D%3D',
            'ul2_cookie': 'eyJ2ZXIiOiIxLjAiLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MzA4NTY3MjgsInVsMl9jb29raWUiOiJ0amMxakxrejU1cWxzazRtT0d0ZXI0WlJEd1cyTGRiajA3dHdtK1NjM0c4PSJ9.UEPh94zQLR7S_NmZIvZouAsI_BR5sqeahQZQaozArvw',
            'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%221306814688555%22%2C%22first_id%22%3A%22192db0cef27694-09582485716d368-26011951-1327104-192db0cef282b4d%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZGIwY2VmMjc2OTQtMDk1ODI0ODU3MTZkMzY4LTI2MDExOTUxLTEzMjcxMDQtMTkyZGIwY2VmMjgyYjRkIiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTMwNjgxNDY4ODU1NSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221306814688555%22%7D%2C%22%24device_id%22%3A%22192db0cef27694-09582485716d368-26011951-1327104-192db0cef282b4d%22%7D',
            '_uetsid': 'bf0c5920965e11ef8cb801b967ef4275',
            '_uetvid': 'bf0c6170965e11ef9896797a3ef0e922',
            '_ga_M0GFGLPMZ2': 'GS1.1.1730251910.1.1.1730251983.51.0.1729803349',
            'GsCookieFlag': '%7B%22pageCont%22%3A1%2C%22globalTimeOut%22%3A1730252072425%2C%22isIndexTop%22%3A%22on%22%7D',
        }

    @staticmethod
    def headers():
        return {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
            'baggage': 'sentry-environment=production,sentry-release=016,sentry-public_key=a320a900b5e049ac8719b0a3247da612,sentry-trace_id=ce20ef4cedc84435b5268815b1c9a97e,sentry-sample_rate=0.1,sentry-transaction=searchList-products,sentry-sampled=false',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            # 'cookie': 'visid_incap_2720266=FFD5otJWSrKz5wawxmoLfoGMIWcAAAAAQUIPAAAAAAApGTYc0f3baOiaHdDxd4ce; incap_ses_1565_2720266=iXueHAjiDAu96uaOYf+3FYGMIWcAAAAABh0AHNU0KG9irbFi3S4+jA==; reese84=3:GrBlPLF89/CsUqJgGN/9XQ==:Oo2jR6nfkXVLDj3QV8MOkSfhlDk4YD/u4mFkcWyl3YmzGugpE/926rL+hf2oEpfvWYDj3P52m8MnbuzqhrNTGlGWbpYwjxgAVOk+4QjU24EduFQo8X40r+pnoIibooRi7uHJ8T+ehV80knRhUpJI3RsOfXrW9DtyfABkb2UFDz1PK3sxoZa0Ih8oS08cdxf80wmjdBCqjPzFt9kyGlVQvSn7+YEzUvOIDIXZl92DsWo+nIDfaIhyGvsey03p+J0XvTpTbFEEg74RV75WVY8oofX9c2GzlkHZvSjt/3PnSzZ0s5Fo5wOmPZ9is/gyFXT5xShtlMVCWuhBxaIFN2qzwL2lFrVb9lPutjfRMn/O3LKuRoInaAavl0/GuJpft20oWAr1xeF9KhxQUnrFfuuNbMp6dvCs7hGwnVab+6R5/XFBej81jeGYROLRzu59QFkH+l0ZD5cJ2FBfdibf75ooa1S4o1dcDWPE9hoHRNNnwEA=:7Zve2kIQBp2lQAk/I2/9JZcXT7K/1YQmuzLuBQb4NpY=; lang=enus; bucket=a; nlbi_2720266=kTU+cNRgZAU0LxSEWlZLAwAAAAABZPe1fOMl1+vxfH5tFOik; _gcl_au=1.1.528652569.1730251909; _ga=GA1.1.1195019572.1730251911; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; nlbi_2720266_2147483392=HSiLK0dONAbsv47mWlZLAwAAAABdwNDJ2+HBXXzom1AEoH1u; visid_incap_2815037=j1zBIqy0RPuO+RU5Opd1oGSMIWcAAAAAQUIPAAAAAABge884mXA7tiW07ulXHBns; nlbi_2815037=er9IFUQTmBSwXOWoQ07hiwAAAABhtAnJB/hox/n2q9623esb; incap_ses_1855_2815037=C6hOGdtGYxuzEIzvwEi+GYyMIWcAAAAAOLZZXddJlXl+XLsEUP1toQ==; _fbp=fb.1.1730251912087.683349651611171710; nlbi_2920482=rT8qaKdPQ2u+kuN/ANt64gAAAAAslRKPwsfBLBmOg9Doa6l5; visid_incap_2920482=g8gWfFGcQU6ryhDNt8aUu42MIWcAAAAAQUIPAAAAAACIz71gB9KcUKeF+ePjTh8Y; incap_ses_1565_2920482=ikPdUdlenCPl8+aOYf+3FY2MIWcAAAAAcdLLbaxkzqApobg7ngLkQw==; ul_cookie=y2tgfQGjQwD3MnaJBmBNUA%3D%3D; ul2_cookie=eyJ2ZXIiOiIxLjAiLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MzA4NTY3MjgsInVsMl9jb29raWUiOiJ0amMxakxrejU1cWxzazRtT0d0ZXI0WlJEd1cyTGRiajA3dHdtK1NjM0c4PSJ9.UEPh94zQLR7S_NmZIvZouAsI_BR5sqeahQZQaozArvw; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221306814688555%22%2C%22first_id%22%3A%22192db0cef27694-09582485716d368-26011951-1327104-192db0cef282b4d%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZGIwY2VmMjc2OTQtMDk1ODI0ODU3MTZkMzY4LTI2MDExOTUxLTEzMjcxMDQtMTkyZGIwY2VmMjgyYjRkIiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTMwNjgxNDY4ODU1NSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221306814688555%22%7D%2C%22%24device_id%22%3A%22192db0cef27694-09582485716d368-26011951-1327104-192db0cef282b4d%22%7D; _uetsid=bf0c5920965e11ef8cb801b967ef4275; _uetvid=bf0c6170965e11ef9896797a3ef0e922; _ga_M0GFGLPMZ2=GS1.1.1730251910.1.1.1730251983.51.0.1729803349; GsCookieFlag=%7B%22pageCont%22%3A1%2C%22globalTimeOut%22%3A1730252072425%2C%22isIndexTop%22%3A%22on%22%7D',
            'lang': 'enus',
            'origin': 'https://www.globalsources.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.globalsources.com/searchList/products?keyWord=phone%20case%20for%20iphone&pageNum=1',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sensorsid': '$device_id=1306814688555',
            'sentry-trace': 'ce20ef4cedc84435b5268815b1c9a97e-bed5a308da2a4ada-0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

    @retry(tries=3, delay=3)
    def get_response(self, url, params=None, json_data=None):
        try:
            response = requests.post(
                url=url,
                cookies=self.generate_cookies(),
                params=params,
                headers=self.headers(),
                json=json_data
            )
            return response
        except Exception as e:
            logger.error(e)

    @staticmethod
    def product_feilds():
        return {
            "product_id": 0,
            "company_name": "",
            "detail_url": "",
            "image_url": "",
            "lead_time": 0,
            "min_order": 0,
            "model_number": "",
            "new_product_flag": "",
            "o2o_flag": "",
            "price": "",
            "publish_date": "",
            "region": "",
            "supplier_id": 0,
            "title": "",
            "unit": ""
        }

    @staticmethod
    def supplier_feilds():
        return {
            'id': '', 'business_type': '', 'company_certs': '', 'contract_group_code': '',
                'global_sources_year': '', 'level': '', 'product_certs': '', 'supplier_location': '',
                'supplier_name': '', 'supplier_short_name': '', 'supplier_type': '', 'usp': '', 'vr_flag': '',
                'vr_video_url': '', 'vr_video_url_cover': '', 'website_name': ''}
