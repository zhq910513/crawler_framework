# -*- coding: utf-8 -*-


import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="QF Payment API",
    description="API for QF payment processing",
    version="1.0.0"
)


# QF类
class QF(object):
    def __init__(self):
        self.session = self.get_session()

    @staticmethod
    def generate_cookies():
        try:
            cookie_cache = {}
            return cookie_cache
        except Exception as e:
            raise ValueError(f"获取 cookies 失败: {str(e)}")

    @staticmethod
    def generate_headers():
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://item-hk.qfapi.com/crp/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    @staticmethod
    def accept_link(link):
        return link.split("link_id=")[1].split("&")[0]

    def get_session(self):
        session = requests.Session()
        cookies = self.generate_cookies()
        headers = self.generate_headers()
        session.cookies.update(cookies)
        session.headers.update(headers)
        return session

    def get_link_base_info(self, _link: str):
        link_id = self.accept_link(_link)
        params = {
            'link_id': link_id,
            'format': 'cors',
        }
        resp_json = self.session.get('https://item-hk.qfapi.com/remotepay/pay/detail', params=params).json()
        return {
            'link_id': str(resp_json["data"]["link_id"]),
            'name': resp_json["data"]["intend_customer"]["name"],
            'mobile': '',
            'memo': '',
            'email': '',
            'detail': '',
            'agree_pact': '2',
            'customer_id': str(resp_json["data"]["intend_customer"]["customer_id"]),
            'address_id': '',
            'return_url': 'https://item-hk.qfapi.com/remotepay/pay/pay_result',
            'failed_url': 'https://item-hk.qfapi.com/remotepay/pay/pay_result',
            'format': 'cors',
        }

    def submit_form_for_payment(self, _data: dict):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://item-hk.qfapi.com',
            'Pragma': 'no-cache',
            'Referer': 'https://item-hk.qfapi.com/crp/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.session.headers.clear()
        self.session.headers.update(headers)

        resp_json = self.session.post('https://item-hk.qfapi.com/remotepay/pay/do_order', data=_data).json()
        payment_info = resp_json["data"]["pay"]
        payment_info["txamt"] = str(payment_info["txamt"])
        return payment_info

    def check_out_info(self, _data: dict):
        headers = {
            'Accept': 'application/json; charset=UTF-8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://openapi-hk.qfapi.com',
            'Pragma': 'no-cache',
            'Referer': 'https://openapi-hk.qfapi.com/checkstand/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.session.headers.clear()
        self.session.headers.update(headers)

        _data.update({
            'lang': 'zh-cn',
            'pay_env': 'pc',
            'format': 'cors',
        })
        resp_json = self.session.post('https://openapi-hk.qfapi.com/checkout/v1/info', data=_data).json()

    def get_payment_link(self, _data: dict):
        headers = {
            'Accept': 'application/json; charset=UTF-8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://openapi-hk.qfapi.com',
            'Pragma': 'no-cache',
            'Referer': 'https://openapi-hk.qfapi.com/checkstand/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.session.headers.clear()
        self.session.headers.update(headers)

        _data.update({
            'pay_type': '801514',
            'format': 'cors',
            'pay_tag': 'ALIPAYCN',
        })
        resp_json = self.session.post('https://openapi-hk.qfapi.com/checkout/v1/payment', headers=headers,
                                      data=_data).json()
        return resp_json["pay_url"]

    def run(self, _link):
        customer_info = self.get_link_base_info(_link=_link)
        payment_info = self.submit_form_for_payment(_data=customer_info)
        return self.get_payment_link(_data=payment_info)


# 定义请求模型
class PaymentRequest(BaseModel):
    link: str


# 创建QF实例
qf = QF()


@app.post("/get_payment")
async def get_payment(request: PaymentRequest):
    try:
        # 直接调用run方法
        result = qf.run(_link=request.link)
        return {"status": "success", "payment_url": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
