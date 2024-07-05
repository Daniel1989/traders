from service.exchange.base import Exchange
import datetime
import requests
import xlrd
import os
import uuid

from models import DailyTraderData

class Zzfe(Exchange):
    def saveWebFileTolocal(self, path, dateStr, type):
        dir = 'daily_data_temp'
        if not os.path.exists(dir):
            os.makedirs(dir)
        resp = requests.get(path)
        file_name = uuid.uuid4().hex + "_" + dateStr + '_zz_' + type + '.xls'
        file_path = dir + "/" + file_name
        output = open(file_path, 'wb')
        output.write(resp.content)
        output.close()
        return file_path

    def handle4DailyRecord(self, dateStr):
        targetPath = 'http://www.czce.com.cn/cn/DFSStaticFiles/Future/' + dateStr[
                                                                          :4] + '/' + dateStr + '/FutureDataDaily.xls'
        path = self.saveWebFileTolocal(targetPath, dateStr, 'record')
        self.handleRecord(path)

    def handleRecord(self, path):
        all_need_save_item_list = []
        wb = xlrd.open_workbook(path)
        sh = wb.sheet_by_index(0)
        date_str = sh.row_values(0)[0][-11:-1]
        good_item_list = []
        good_item_single_detail = []
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        for i in range(sh.nrows):
            if i == 0 or i == 1:
                continue
            if sh.row_values(i)[0] == '总计':
                break
            else:
                good_item_single_detail.append(sh.row_values(i))
                if '小计' == sh.row_values(i)[0]:
                    good_item_list.append(good_item_single_detail)
                    good_item_single_detail = []
        # 合约只补20年代的
        year = int(datetime.datetime.now().strftime('%Y'))
        if year > 2029:
            raise Exception("自动补调的合约号需要更新")
        autofill_year = '2'
        for item in good_item_list:
            good_code = item[0][0][:2]
            # number = re.findall(r'\d+', '1TB') 1
            # unit = re.findall(r'\D+', '1TB') TB
            for record in item[:-1]:
                percent = float(self.formatNumberValue(record[7])) / float(self.formatNumberValue(record[1]))
                all_need_save_item_list.append(
                    [good_code, autofill_year + record[0][2:], date, self.formatNumberValue(record[2]),
                     self.formatNumberValue(record[3]), self.formatNumberValue(record[4]),
                     self.formatNumberValue(record[5]), \
                     self.formatNumberValue(record[6]), self.formatNumberValue(record[7]),
                     self.formatNumberValue(record[8]), self.formatNumberValue(record[9]),
                     float(self.formatNumberValue(record[12])), self.formatNumberValue(record[10]), percent, good_code
                     ])
        for item in all_need_save_item_list:
            try:
                DailyTraderData.create(goods=item[0], code_no=item[1], date=item[2], open_price=item[3],
                                    highest_price=item[4], \
                                    lowest_price=item[5], close_price=item[6], compute_price=item[7], diff1=item[8], \
                                    diff2=item[9], deal_vol=item[10], amount=item[11], have_vol=item[12],
                                    percent=item[13], symbol=str(item[14]).upper(), exchange='zz')
            except Exception as e:
                print("数据保存出错，跳过保存，出错数据", item)
                print("出错原因", e)
