import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from models import Ip
import time
import datetime
from dotenv import load_dotenv
import os

from service.ip import get_high_score_ip
from util.utils import is_trade_time

load_dotenv()
proxy_token = os.getenv("PROXY_TOKEN") or ""


class Crawl:
    def __init__(self, base_url, goods_code):
        self.base_url = base_url
        self.goods_code = goods_code
        self.status = "init"
        self.retry_num = 0
        self.proxypool_url = "http://47.96.156.119/proxy/random?token=" + proxy_token
        self.use_proxy = False

    def get_random_proxy(self):
        return requests.get(self.proxypool_url).text.strip()

    def build_url(self):
        return self.base_url + "/" + self.goods_code + ".shtml"

    def parse_page(self, page):
        url = self.build_url()
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        data = page.request.get(
            "https://hq.sinajs.cn/etag.php?_=" + str(timestamp) + "&list=nf_" + self.goods_code, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Host": "hq.sinajs.cn",
                "Referer": url,
            })
        content = data.body().decode("GB2312").split("=")[1]
        price = content.replace('"', '').split(",")
        print("price is:", price)

    def do_crawl(self, use_proxy=False):
        with sync_playwright() as p:
            for browser_type in [p.chromium]:  # p.firefox, p.webkit
                try:
                    success_ip = get_high_score_ip()
                    if success_ip:
                        proxy = success_ip.ip
                    else:
                        proxy = 'http://' + self.get_random_proxy()
                    print("proxy is:", proxy)
                    browser = browser_type.launch(proxy={
                        "server": proxy
                    })
                    page = browser.new_page()
                    try:
                        start_time = datetime.datetime.now()
                        self.parse_page(page)
                        end_time = datetime.datetime.now()
                        if self.use_proxy or use_proxy:
                            if success_ip:
                                success_ip.success_num += 1
                                success_ip.last_check_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                success_ip.status = "success"
                                success_ip.cost_time = int((end_time - start_time).total_seconds() * 1000)
                                success_ip.save()
                            else:
                                available_ip = Ip(ip=proxy, cost_time=int((end_time - start_time).total_seconds() * 1000), status="success", success_num=1, fail_num=0,
                                                  last_check_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                available_ip.save()
                    except Exception as e:
                        if self.use_proxy or use_proxy:
                            if success_ip:
                                success_ip.fail_num += 1
                                success_ip.last_check_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                success_ip.status = "fail"
                                success_ip.cost_time = -1
                                success_ip.save()
                            else:
                                available_ip = Ip(ip=proxy, cost_time=-1,
                                                  status="fail", success_num=0, fail_num=1,
                                                  last_check_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                available_ip.save()
                        print("parse page error", e)
                    browser.close()
                except Exception as e:
                    print("执行出错", e)


if __name__ == "__main__":
    goods = "AG2408"
    futureCrawler = Crawl("https://finance.sina.com.cn/futures/quotes", goods)
    while True:
        futureCrawler.do_crawl(use_proxy=True)
        time.sleep(60)
