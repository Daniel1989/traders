import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from models import GoodsPriceInSecond, Goods
import time
import datetime
from dotenv import load_dotenv
import os
import traceback

from util.utils import is_trade_time

load_dotenv()
proxy_token = os.getenv("PROXY_TOKEN") or ""

price_model_key_list = ['uid', 'goods', 'price_time', 'current_price', 'price_diff',
                        'price_diff_percent', 'close_price', 'open_price',
                        'high_price', 'low_price',
                        'compute_price', 'prev_compute_price',
                        'have_vol', 'deal_vol', 'buy_price_oncall', 'sell_price_oncall',
                        'buy_vol', 'sell_vol',
                        ]

def is_debian():
    try:
        with open("/etc/os-release", "r") as file:
            os_info = file.read().lower()
            return "debian" in os_info
    except FileNotFoundError:
        return False

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
        goods = Goods.select().where(Goods.name == self.goods_code[:2]).get()
        url = self.build_url()

        page.goto(url)
        page.wait_for_selector(".min-price")
        while True:
            content = page.evaluate("""
                () => {
          return document.getElementById("table-box-futures-hq").innerHTML
        }
                """)
            soup = BeautifulSoup('<div>' + content + '</div>', 'html.parser')
            trs = soup.find_all("tr")
            price_detail = [self.goods_code, goods.id]
            for index, tr in enumerate(trs):
                th = tr.find_all("th")
                td = tr.find_all("td")
                if index == 3:
                    continue
                else:
                    if index == 0:
                        first = td.pop(0)
                        trade_time = first.find(class_='trade-time').text
                        current_price = first.find(class_='price').text
                        price_diff = first.find(class_='amt-value').text.replace("+", "").replace("-", "")
                        price_diff_percent = first.find(class_='amt').text.replace("+", "") \
                            .replace("-", "").replace("%", "")
                        price_detail.append(trade_time)
                        price_detail.append(current_price)
                        price_detail.append(price_diff)
                        price_detail.append(price_diff_percent)
                    for h, d in zip(th, td):
                        if len(h.text.strip()) > 0:
                            price_detail.append(d.text)
                            print(h.text.strip().replace("&nbsp;", "").replace(u'\xa0', "").replace(":", ""),
                                  d.text.strip())
            info = {}
            for item in price_model_key_list:
                info[item] = price_detail.pop(0)
            record = GoodsPriceInSecond(**info)
            record.save()
            time.sleep(5)
            # 判断是否交易时间，不是则跳出
            if not is_trade_time():
                break

    def do_crawl(self):
        with sync_playwright() as p:
            target = p.webkit if is_debian() else p.chromium
            for browser_type in [target]:  # p.firefox, p.chromium, p.webkit
                try:
                    browser = browser_type.launch()
                    page = browser.new_page()
                    try:
                        self.parse_page(page)
                    except Exception as e:
                        print("parse page error", e)
                        traceback.print_exc()

                    # page.goto('https://api.ipify.org?format=json')
                    # response = page.evaluate("document.body.textContent")
                    # print(f"Public IP Address: {response}")
                    # user_agent = page.evaluate("navigator.userAgent")
                    browser.close()
                except Exception as e:
                    print("执行出错", e)
                    traceback.print_exc()


if __name__ == "__main__":
    futureCrawler = Crawl("https://finance.sina.com.cn/futures/quotes", "AG2408")
    while True:
        today = datetime.date.today()
        if today.weekday() != 5 or today.weekday() != 6:  # Saturday
            if is_trade_time():
                futureCrawler.do_crawl()
            else:
                print("非交易时间")
        else:
            print("休市")
        time.sleep(60)
