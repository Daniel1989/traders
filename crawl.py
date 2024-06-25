import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from models import PriceRecord, Goods
import time
import datetime


class Crawl:
    def __init__(self, base_url, goods_code):
        self.base_url = base_url
        self.goods_code = goods_code
        self.status = "init"
        self.retry_num = 0
        self.proxypool_url = 'http://127.0.0.1:5555/random'
        self.use_proxy = False

    def get_random_proxy(self):
        return requests.get(self.proxypool_url).text.strip()

    def build_url(self):
        return self.base_url + "/" + self.goods_code + ".shtml"

    def do_crawl(self):
        goods = Goods.select().where(Goods.name == self.goods_code[:2]).get()
        url = self.build_url()
        with sync_playwright() as p:
            for browser_type in [p.chromium]:  # p.firefox, p.webkit
                try:
                    if self.use_proxy:
                        proxy = 'http://' + self.get_random_proxy()
                        browser = browser_type.launch(proxy={
                            "server": proxy
                        })
                    else:
                        browser = browser_type.launch()

                    page = browser.new_page()
                    # page.goto('https://api.ipify.org?format=json')
                    # response = page.evaluate("document.body.textContent")
                    # print(f"Public IP Address: {response}")
                    # user_agent = page.evaluate("navigator.userAgent")

                    page.goto(url)
                    element_id = "table-box-futures-hq"
                    page.wait_for_selector(f'#{element_id}')
                    content = page.inner_html(f'#{element_id}')
                    soup = BeautifulSoup('<div>' + content + '</div>', 'html.parser')
                    trs = soup.find_all("tr")
                    # hidden_tr_elements = [tr for tr in tr_elements if
                    #                       'style' in tr.attrs and 'display: none' in tr.attrs['style']]

                    for index, tr in enumerate(trs):
                        if index != 0:
                            continue
                        th = tr.find_all("th")
                        td = tr.find_all("td")
                        if len(th) != len(td):
                            first = td.pop(0)
                            data = first.text.strip().split("\n")
                            record = PriceRecord(goods=goods.id,
                                                 price=float(data[0]),
                                                 date=data[3].split(" ")[0],
                                                 type="1MIN",
                                                 timestamp=data[3].split(" ")[1])
                            record.save()
                        # for h, d in zip(th, td):
                        #     if len(h.text.strip()) > 0:
                        #         print(h.text.strip().replace("&nbsp;", ""), d.text.strip())
                    browser.close()
                except Exception as e:
                    print("执行出错", e)


def is_time_in_range(start, end, now=None):
    # If now is not specified, use current time
    now = now or datetime.datetime.now().time()
    if start <= end:
        return start <= now <= end
    else:  # crosses midnight
        return start <= now or now <= end


def is_time_in_day_range(start, end, now=None):
    # If now is not specified, use current time
    now = now or datetime.datetime.now().time()

    # Convert start and end times to datetime objects for comparison
    start_dt = datetime.datetime.combine(datetime.date.today(), start)
    end_dt = datetime.datetime.combine(datetime.date.today(), end)
    now_dt = datetime.datetime.combine(datetime.date.today(), now)

    if start <= end:
        return start_dt <= now_dt <= end_dt
    else:  # crosses midnight
        return start_dt <= now_dt or now_dt <= end_dt


def is_trade_time():
    start_morning = datetime.time(9, 0)
    end_morning = datetime.time(11, 30)

    start_afternoon = datetime.time(13, 30)
    end_afternoon = datetime.time(15, 00)

    start_time = datetime.time(21, 0)  # 10:00 PM
    end_time = datetime.time(2, 0)

    return (is_time_in_range(start_morning, end_morning) or
            is_time_in_range(start_afternoon, end_afternoon) or
            is_time_in_day_range(start_time, end_time)
            )


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

        time.sleep(5 * 60)
