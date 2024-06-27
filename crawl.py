import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from models import PriceRecord, Goods, Ip
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

    def parse_page(self, page, use_proxy=False):
        goods = Goods.select().where(Goods.name == self.goods_code[:2]).get()
        url = self.build_url()
        timestamp = int(datetime.datetime.now().timestamp() * 1000)

        # TODO 这里使用循环，看是否能等价于打开页面不停的内容
        # page.goto(url)
        # page.wait_for_selector(".min-price")
        # for i in range(100000):
        #     text = page.evaluate("""
        #         () => {
        #   return document.getElementsByClassName("min-price")[0].innerHTML
        # }
        #         """)
        #     print(text)

        data = page.request.get(
            "https://hq.sinajs.cn/etag.php?_=" + str(timestamp) + "&list=nf_" + self.goods_code, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Host": "hq.sinajs.cn",
                "Referer": url,
            })
        content = data.body().decode("GB2312").split("=")[1]
        price = content.replace('"', '').split(",")
        print("price is:", price)
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        if use_proxy:
            record = PriceRecord(goods=goods.id,
                                 price=float(price[7]),
                                 type="5MIN",
                                 timestamp=formatted_time.split(" ")[1])
            record.save()

    def do_crawl(self, use_proxy=False):

        with sync_playwright() as p:
            for browser_type in [p.chromium]:  # p.firefox, p.webkit
                try:
                    if self.use_proxy or use_proxy:
                        success_ip = get_high_score_ip()
                        if success_ip:
                            proxy = success_ip.ip
                        else:
                            proxy = 'http://' + self.get_random_proxy()
                        print("proxy is:", proxy)
                        browser = browser_type.launch(proxy={
                            "server": proxy
                        })
                    else:
                        print("no proxy")
                        browser = browser_type.launch()

                    page = browser.new_page()
                    try:
                        start_time = datetime.datetime.now()
                        self.parse_page(page, self.use_proxy or use_proxy)
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
                                                  last_check_time=datetime.datetime.now())
                                available_ip.save()
                        print("parse page error", e)

                    # page.goto('https://api.ipify.org?format=json')
                    # response = page.evaluate("document.body.textContent")
                    # print(f"Public IP Address: {response}")
                    # user_agent = page.evaluate("navigator.userAgent")

                    # page.goto(url)

                    # page.wait_for_load_state('networkidle')
                    # element_id = "table-box-futures-hq"
                    # page.wait_for_selector(f'#{element_id}')
                    # content = page.inner_html(f'#{element_id}')
                    # soup = BeautifulSoup('<div>' + content + '</div>', 'html.parser')
                    # trs = soup.find_all("tr")
                    # for index, tr in enumerate(trs):
                    #     if index != 0:
                    #         continue
                    #     th = tr.find_all("th")
                    #     td = tr.find_all("td")
                    #     if len(th) != len(td):
                    #         first = td.pop(0)
                    #         data = first.text.strip().split("\n")
                    #         print("data is", data)
                    #         record = PriceRecord(goods=goods.id,
                    #                              price=float(data[0]),
                    #                              date=data[3].split(" ")[0],
                    #                              type="1MIN",
                    #                              timestamp=data[3].split(" ")[1])
                    #         record.save()
                    # for h, d in zip(th, td):
                    #     if len(h.text.strip()) > 0:
                    #         print(h.text.strip().replace("&nbsp;", ""), d.text.strip())
                    browser.close()
                except Exception as e:
                    print("执行出错", e)


if __name__ == "__main__":
    futureCrawler = Crawl("https://finance.sina.com.cn/futures/quotes", "AG2408")
    while True:
        today = datetime.date.today()
        if today.weekday() != 5 or today.weekday() != 6:  # Saturday
            if is_trade_time():
                futureCrawler.do_crawl()
                futureCrawler.do_crawl(use_proxy=True)
            else:
                print("非交易时间")
        else:
            print("休市")

        time.sleep(5 * 60)
