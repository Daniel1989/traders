from models import DailyTraderData
from service.exchange.base import Exchange
import datetime
import requests
import json
import traceback

requests.packages.urllib3.util.connection.HAS_IPV6 = False

headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    "Host": "www.gfex.com.cn",
    "Origin": "http://www.gfex.com.cn",
    "Referer": "http://www.gfex.com.cn/gfex/rihq/hqsj_tjsj.shtml",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}


class Gzfe(Exchange):
    def getTradeData(self, date_str):
        url = "http://www.gfex.com.cn/u/interfacesWebTiDayQuotes/loadList"
        payload = {
            'trade_date': date_str,
            'trade_type': 0
        }
        response = requests.post(url, data=payload, headers=headers)
        html_content = response.text
        return json.loads(html_content)

    def doSave4Record(self, item):
        try:
            DailyTraderData.create(goods=item[0], code_no=item[1], date=item[2], open_price=item[3],
                                   highest_price=item[4],
                                   lowest_price=item[5], close_price=item[6], compute_price=item[7], diff1=item[8],
                                   diff2=item[9], deal_vol=item[10], amount=item[12], have_vol=item[11],
                                   percent=item[13], symbol=str(item[14]).upper(), exchange='gz')
        except Exception as e:
            traceback.print_exc()
            print("数据保存出错，跳过保存，出错数据", item)
            print("出错原因", e)

    def convertCsvToModel(self, good, date, record, percent):
        return [good, record[0], date, self.formatNumberValue(record[2]), self.formatNumberValue(record[3]),
                self.formatNumberValue(record[4]), self.formatNumberValue(record[5]), \
                self.formatNumberValue(record[6]), record[7], record[8], self.formatNumberValue(record[9]),
                self.formatNumberValue(float(record[10])), self.formatNumberValue(record[11]), percent, record[13]]

    def handle4DailyRecord(self, dateStr):
        jsonContent = self.getTradeData(dateStr)
        date = str(datetime.datetime.strptime(dateStr, '%Y%m%d'))
        all_need_save_item_list = []

        for item in jsonContent['data']:
            if item['variety'] == "工业硅" or item['variety'] == "碳酸锂":
                record = [
                    item['delivMonth'],
                    item['lastClear'],
                    item['open'],
                    item['high'],
                    item['low'],
                    item['close'],
                    item['clearPrice'],
                    item['diff'],
                    item['diff1'],
                    item['volumn'],
                    item['openInterest'],
                    item['diffI'],
                    item['turnover'],
                    item['varietyOrder']
                ]
                percent = float(record[7]) / float(record[1])
                all_need_save_item_list.append(self.convertCsvToModel(item['variety'], date, record, percent))

        for item in all_need_save_item_list:
            self.doSave4Record(item)
