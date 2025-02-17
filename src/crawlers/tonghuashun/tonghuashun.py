import logging
from urllib.parse import urlencode
import requests
from crawlers.tonghuashun import get_headers, headers
import requests
import sys
import json
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd

from utils.common import convert_to_number


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


def trading_leaders_board_total_page(url):
        headers = get_headers()
        response = requests.get(url=url, headers=headers)
        text = response.text
        logger.info(text)
        total_page = get_by_last_page(text)
        if total_page is None or total_page <= 0:
               raise ValueError(f'爬取龙虎榜数据出错：{url}')
        return total_page

# 龙虎榜数据
def parse_yyb_trading(yyb_url):
        # 先爬取页数
        # yyb_url = 'https://data.10jqka.com.cn/ifmarket/lhbhistory/orgcode/83ab38bef23d4d98'
        total_page = trading_leaders_board_total_page(yyb_url)
        for i in range(1, total_page + 1):
                if i == 3:
                       break
                url = f'{yyb_url}field/ENDDATE/order/desc/page/{i}/'
                headers = get_headers()
                response = requests.get(url=url, headers=headers)
                text = response.text
                logger.debug(text)
                df = parse_yyb_trading_html(text)
                print(df)
                return df

def parse_yyb_trading_html(html: str):
        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='m-table')

        # 提取表头
        headers = [th.get_text(strip=True) for th in table.thead.find_all('th')]

        # 提取表格数据
        rows = []
        for tr in table.tbody.find_all('tr'):
                tds = tr.find_all('td')

                # 确保列数正确
                if len(tds) != 8:
                        continue

                # 处理每一列数据
                date = tds[0].get_text(strip=True)
                stock = tds[1].find('a').get_text(strip=True)  # 提取股票简称链接文本
                reason = tds[2].get_text(strip=True)
                change = float(tds[3].get_text(strip=True))
                buy = float(tds[4].get_text(strip=True))
                sell = float(tds[5].get_text(strip=True))
                net = float(tds[6].get_text(strip=True))
                sector = tds[7].get_text(strip=True)

                rows.append([date, stock, reason, change, buy, sell, net, sector])

        # 创建DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # 优化数据类型
        df['上榜日期'] = pd.to_datetime(df['上榜日期'])
        numeric_cols = ['涨跌幅(%)', '买入额（万）', '卖出额（万）', '买卖净额（万）']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

        return df



def get_by_last_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    last_page = soup.find('a', class_='changePage', string='尾页')
    if last_page and last_page.has_attr('data-param'):
        try:
            return int(last_page['data-param'])
        except ValueError:
            pass
    return None

def get_longhu():
        url = 'https://data.10jqka.com.cn/market/longhu/'
        headers = get_headers()
        response = requests.get(url=url, headers=headers)
        text = response.text
        logger.debug(text)
        if not text:
               raise ValueError(f"爬取龙虎榜主页失败：{url}")
        return text


# 龙虎榜-营业部
def get_yyb_list(page):
        url = f'https://data.10jqka.com.cn/ifmarket/lhbyyb/type/1/tab/sbcs/field/sbcs/sort/desc/page/{page}/'
        headers = get_headers()
        response = requests.get(url=url, headers=headers)
        text = response.text
        logger.debug(text)
        df = parse_yyb_table(text)
        return df

def parse_yyb_table(html):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='m-table')
        if not table:
                raise ValueError("未找到 <div class='yyb'> 内的表格")
        headers = [header.get_text(strip=True) for header in table.select('thead th')]
        headers.append("营业部链接")
        # 提取表格数据
        rows = []
        for row in table.select('tbody tr'):
                cells = row.find_all('td')
                # 提取每个单元格的内容
                row_data = [
                        convert_to_number(cell.get_text(strip=True).replace('...', '')) if not cell.find('a') else cell.a['title']
                        for cell in cells
                ]
                # 提取营业部链接
                link = cells[1].find('a')['href'] if cells[1].find('a') else None
                row_data.append(link)
                rows.append(row_data)

        # 创建 DataFrame
        df = pd.DataFrame(rows, columns=headers)
        return df
def orgcode_from_url(url):
       return url.split("/")[-1]

def parse_yyb(html: str):
        soup = BeautifulSoup(html, 'html.parser')
        # 定位到 <div class="yyb"> 内的表格
        target_div = soup.find('div', class_='yyb')
        if not target_div:
                raise ValueError("未找到 <div class='yyb'> 元素")

        # 提取表格数据
        table = target_div.find('table', class_='m-table')
        if not table:
                raise ValueError("未找到 <div class='yyb'> 内的表格")
        pagination = target_div.find('div', class_='m-pager')
        if not pagination:
                raise ValueError("未找到 <div class='yyb'> 内的分页数据")
        last_page = soup.find('a', class_='changePage', string='尾页')
        page_num = 0
        if last_page and last_page.has_attr('data-param'):
                try:
                        page_num = int(last_page['data-param'])
                except ValueError:
                        raise ValueError("提取 <div class='yyb'> 内的分页数据失败")
        for i in range(1, page_num + 1):
                df = get_yyb_list(i)
                yield df

def parse_trading_leaders_board():
        pass

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