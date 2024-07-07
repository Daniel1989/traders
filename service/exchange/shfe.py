from service.exchange.base import Exchange
import datetime
import json
import traceback
import requests

from models import DailyTraderData
import time

from util.notify import send_common_to_ding


class Shfe(Exchange):
    def crawl_data(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                'Host': 'www.shfe.com.cn',
                'Referer': 'https://www.shfe.com.cn/reports/marketdata/delayedquotes/'
            }
            res = requests.get('https://www.shfe.com.cn/data/tradedata/future/delaymarket/delaymarket_all.dat?params='+ str(int(time.time() * 1000)), headers=headers)
            data = json.loads(res.text)
            flatten_list = [item for sublist in data["delaymarket"] for item in sublist]
            return [{
                **item,
                "open_price": item["openprice"],
                "high_price": item["highprice"],
                "low_price": item["lowerprice"],
                "close_price": item["lastprice"],
                "deal_vol": item["volume"],
                "data_time": item["updatetime"],
                "contract_number": "".join(item["contractname"][-4:]),
                "goods_code": item["instrumentid"].upper(),
                "current_price": float(item["lastprice"]),
            } for item in flatten_list if item["contractname"]!="IMCI"]
        except Exception as e:
            send_common_to_ding("获取上海交易所分钟数据出错，出错原因：" + e.__str__())
            return []


    def doSave4Record(self, item):
        try:
            DailyTraderData.create(goods=item[0], code_no=item[1], date=item[2], open_price=item[3], highest_price=item[4], \
                                lowest_price=item[5], close_price=item[6], compute_price=item[7], diff1=item[8], \
                                diff2=item[9], deal_vol=item[10], amount=item[11], have_vol=item[12], percent=item[13], symbol=str(item[14]).upper(), exchange='sh')
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
        date = str(datetime.datetime.strptime(dateStr, '%Y%m%d'))
        response = self.session.get('https://www.shfe.com.cn/data/tradedata/future/dailydata/kx' + dateStr + '.dat')
        content = response.content.decode('utf_8-sig')
        jsonContent = json.loads(content)
        all_need_save_item_list = []
        for item in jsonContent['o_curinstrument']:
            if item['DELIVERYMONTH'] == '小计' or item['PRODUCTID'].strip() in ['总计', 'sc_tas', 'ssefp'] \
                    or 'efp' in item['PRODUCTID']:
                continue
            record = [
                item['DELIVERYMONTH'],
                item['PRESETTLEMENTPRICE'],
                item['OPENPRICE'],
                item['HIGHESTPRICE'],
                item['LOWESTPRICE'],
                item['CLOSEPRICE'],
                item['SETTLEMENTPRICE'],
                item['ZD1_CHG'],
                item['ZD2_CHG'],
                item['VOLUME'],
                item['TURNOVER'],
                item['OPENINTEREST'],
                item['OPENINTERESTCHG'],
                item['PRODUCTGROUPID']
            ]
            percent = float(record[7]) / float(record[1])
            all_need_save_item_list.append(self.convertCsvToModel(item['PRODUCTNAME'], date, record, percent))

        for item in all_need_save_item_list:
            self.doSave4Record(item)




