import logging
from urllib.parse import urlencode
import requests
from crawlers.tonghuashun import headers
import requests
import sys
import json
from pprint import pprint


logger = logging.getLogger(__name__)





'''
#-------------------- 文件说明 --------------------#
        author: gtc_design
        time  : 2025-01-17
        brief :
                # 爬取大盘等相关数据
'''


# 获取同花顺热门股票数据
def get_glamour_stocks():
        url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock?stock_type=a&type=hour&list_type=normal'
        response = requests.get(url=url, headers=headers())
        if response.status_code == 200:
            pass
        else:
            raise Exception("fail to get and the status code: {:s}".format(response.status_code))

        html = response.text

        data = json.loads(html)
        data_strings = []

        for stock_info in data["data"]["stock_list"]:
                name = stock_info.get("name")
                rise_and_fall = stock_info.get("rise_and_fall")

                if (name is not None and rise_and_fall is not None):
                        data_strings.append([name, rise_and_fall])
        if (0):
                for i in range (1, len(data_strings)):
                        print("{:d}: {:s}\t {:4.1f}%".format(i, data_strings[i-1][0], data_strings[i-1][1]))

        return data_strings


# 获取同花顺热门板块
def get_favored_sectors():
        url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/plate?type=concept'
        # 发送请求
        response = requests.get(url=url, headers=headers())

        # 检查是否成功
        if response.status_code == 200:
                pass
        else:
                print("fail to get and the status code: {:s}".format(response.status_code))
                sys.exit(1)
        html = response.text
        data = json.loads(html) # 返回嵌套字典结构
        data_strings = []       # 数据存放列表

        for sectors_info in data["data"]["plate_list"]:
                name = sectors_info.get("name")
                if(name is not None):
                        data_strings.append(name)

        if (0):
                # 打印检查
                for i in range (1, len(data_strings)):
                        print("{:d}: {:s}\t".format(i, data_strings[i-1]))

        return data_strings


# 获取大盘数据
def get_SSE_datas():
        """ 发送请求 """
        # 模拟游览器
        headers = {
                'referer'       : 'https://finance.sina.com.cn/stock/',
                'user-agent'    : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
        }
        # 请求网址
        url = 'https://hq.sinajs.cn/rn=1737181300898&list=s_sh000001,s_sz399001,s_sh000300,s_bj899050,s_sz399006'

        # 参数
        params = {

        }
        # 发送请求
        response = requests.get(url=url, headers=headers, params=params)

        # 检查是否成功
        if response.status_code == 200:
                pass
        else:
            return ''
        html = response.text
        data = html.split(",", )
        data_strings = []               # 存放数据列表

        data_strings.append("上证指数")

        for i in range (1, 4):
                data[i] = float(data[i])
                data_strings.append(data[i])

        # 打印检查
        if (0):
                print(data_strings)

        return data_strings


# 数据整合为一个字典
def trim_datas():
        glamour_list    = get_glamour_stocks()
        favored_list    = get_favored_sectors()
        SSE_list        = get_SSE_datas()

        total_data_dict = {}

        # 整合数据
        total_data_dict.update({"上证指数": SSE_list, "热榜股票": glamour_list, "热门板块": favored_list})

        return total_data_dict


if __name__ == "__main__":

        # 展示热门股票
        if(0):
                data_strings = get_glamour_stocks()
                total_rise = 0

                for i in range (1, 10):
                        print("{:d}: {:s}\t {:4.1f}%".format(i, data_strings[i-1][0], data_strings[i-1][1]))
                        total_rise = total_rise +data_strings[i-1][1]
                average = total_rise/9
                if(average >= 0):
                        print("+{:4.1f} %".format(average))
                else:
                        print("{:4.1f}%".format(average))


        # 展示热门板块
        if(0):
                data_strings = get_favored_sectors()

                for i in range(1, len(data_strings)):
                        print("{:d}: {:s}".format(i, data_strings[i-1]))


        # 展示上证指数数据
        if(0):
                data_strings = get_SSE_datas()
                print(data_strings)


        # 展示所有数据
        if(0):
                data_dict = trim_datas()
                pprint(data_dict)