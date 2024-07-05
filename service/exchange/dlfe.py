import re

from models import DailyTraderData
from service.exchange.base import Exchange
import datetime
import requests
import xlrd
import os
import uuid


class Dlfe(Exchange):

    def saveWebFileTolocal(self, url, dateStr, type, file_type, form_data):
        dir = 'daily_data_temp'
        resp = requests.post(url, data=form_data)
        if not os.path.exists(dir):
            os.makedirs(dir)
        file_name = uuid.uuid4().hex + "_" + dateStr + '_dl_' + type + file_type
        file_path = dir + "/" + file_name
        output = open(file_path, 'wb')
        output.write(resp.content)
        output.close()
        return file_path

    def handle4DailyRecord(self, dateStr):
        url = 'http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html'
        form_data = {
            'dayQuotes.variety': 'all',
            'dayQuotes.trade_type': 0,
            'year': dateStr[:4],
            'month': str(int(dateStr[4:6]) - 1),
            'day': str(int(dateStr[6:])),
            'exportFlag': 'excel'
        }
        path = self.saveWebFileTolocal(url, dateStr, 'record', '.xls', form_data)
        self.handleRecord(path, dateStr)

    def handleRecord(self, path, file_name):
        date_str = file_name.split("_")[0]
        all_need_save_item_list = []

        wb = xlrd.open_workbook(path)
        sh = wb.sheet_by_index(0)
        good_item_list = []
        good_item_single_detail = []
        date = datetime.datetime.strptime(date_str, '%Y%m%d')
        for i in range(sh.nrows):
            if i == 0 or i == 1:
                continue
            if sh.row_values(i)[0] == '总计':
                break
            else:
                good_item_single_detail.append(sh.row_values(i))
                if '小计' in sh.row_values(i)[0]:
                    good_item_list.append(good_item_single_detail)
                    good_item_single_detail = []

        for item in good_item_list:
            good_name = item[0][0]
            symbol = "".join(re.findall(r'[a-zA-Z]', item[0][1]))
            if good_name == '商品名称':
                continue
            for record in item[:-1]:
                percent = float(self.formatNumberValue(record[8])) / float(self.formatNumberValue(record[6]))
                all_need_save_item_list.append(
                    [good_name, record[1], date, self.formatNumberValue(record[2]), self.formatNumberValue(record[3]),
                     self.formatNumberValue(record[4]), self.formatNumberValue(record[5]), \
                     self.formatNumberValue(record[7]), self.formatNumberValue(record[8]),
                     self.formatNumberValue(record[9]), self.formatNumberValue(record[10]),
                     float(self.formatNumberValue(record[13])), self.formatNumberValue(record[11]), percent, symbol
                     ])
        for item in all_need_save_item_list:
            try:
                DailyTraderData.create(goods=item[0], code_no=item[1][-4:], date=item[2], open_price=item[3],
                                    highest_price=item[4], \
                                    lowest_price=item[5], close_price=item[6], compute_price=item[7], diff1=item[8], \
                                    diff2=item[9], deal_vol=item[10], amount=item[11], have_vol=item[12],
                                    percent=item[13], symbol=str(item[14]).upper(), exchange='dl')
            except Exception as e:
                print("数据保存出错，跳过保存，出错数据", item)
                print("出错原因", e)
