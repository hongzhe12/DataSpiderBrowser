# spider.py

import re
import time
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

from crawlers.base_spider import BaseSpider  # 假设 BaseSpider 在 crawlers/base_spider.py
from service.storage import cookie


class JdOrderSpider(BaseSpider):
    """
    京东订单爬虫
    功能：登录后爬取用户的订单列表，提取订单信息并保存为表格数据。
    """

    def get_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤掉 None 或空字典 {}"""
        return data

    def __init__(self, cookies: Dict[str, str], start_page: int = 1, end_page: int = None):
        """
        初始化爬虫。

        Args:
            cookies (Dict[str, str]): 登录京东后的 Cookie 字典。
            start_page (int): 起始页码。
            end_page (int): 结束页码，None 表示爬取到无数据为止。
        """
        self.cookies = cookies
        self.start_page = start_page
        self.end_page = end_page
        self.current_page = start_page

        # 京东订单列表 URL
        self.base_url = "https://order.jd.com/center/list.action"

        # 请求头
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        }

        # 调用父类初始化
        super().__init__(
            name="jd_order_spider",
            start_urls=[f"{self.base_url}?page={start_page}"],
            delay=1.5  # 避免请求过快
        )

    def start_requests(self) -> List[str]:
        """生成起始请求 URL 列表（从 start_page 开始）"""
        if self.end_page and self.end_page < self.start_page:
            return []
        # 我们不在此处生成所有页码，而是在 crawl 过程中动态判断
        return [f"{self.base_url}?page={self.start_page}"]

    def parse(self, response: requests.Response, **kwargs) -> List[Dict[str, Any]]:
        """
        解析京东订单页面 HTML，提取订单信息。
        此方法直接复用了 spider1.py 中的核心解析逻辑。
        """
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            orders = []

            # 查找所有订单的 tbody 元素
            order_tbodies = soup.find_all('tbody', id=re.compile(r'^tb-'))

            for tbody in order_tbodies:
                order = self._extract_order_info(tbody)
                if order:
                    orders.append(order)

            return orders

        except Exception as e:
            print(f"解析页面时出错: {e}")
            return []

    def _extract_order_info(self, tbody) -> Dict[str, Any]:
        """从单个订单 tbody 中提取信息（私有方法）"""
        try:
            order = {}

            tr_th = tbody.find('tr', class_='tr-th')
            if not tr_th:
                return {}

            # 订单号
            order_link = tr_th.find('a', {'name': 'orderIdLinks'})
            if order_link:
                order['order_id'] = order_link.text.strip()
                order['order_url'] = order_link.get('href', '')

            # 订单时间
            dealtime_span = tr_th.find('span', class_='dealtime')
            if dealtime_span:
                order['order_time'] = dealtime_span.get('title', '').strip()

            # 店铺名称
            shop_span = tr_th.find('span', class_='order-shop')
            if shop_span:
                shop_link = shop_span.find('a', class_='shop-txt')
                if shop_link:
                    order['shop_name'] = shop_link.text.strip()

            # 商品信息
            tr_bd = tbody.find('tr', class_='tr-bd')
            if tr_bd:
                goods_item = tr_bd.find('div', class_='goods-item')
                if goods_item:
                    product_name = goods_item.find('a', class_='a-link')
                    if product_name:
                        order['product_name'] = product_name.get('title', '').strip()
                        order['product_url'] = "https:" + product_name.get('href', '')

                    # 商品数量
                    goods_number = goods_item.find_next_sibling('div', class_='goods-number')
                    if goods_number:
                        quantity_text = goods_number.text.strip()
                        match = re.search(r'x(\d+)', quantity_text)
                        if match:
                            order['quantity'] = int(match.group(1))

                # 收货人
                consignee_div = tr_bd.find('div', class_='consignee')
                if consignee_div:
                    consignee_span = consignee_div.find('span', class_='txt')
                    if consignee_span:
                        order['consignee'] = consignee_span.text.strip()

                    prompt_div = consignee_div.find('div', class_='prompt-01')
                    if prompt_div:
                        address_p = prompt_div.find('p')
                        if address_p:
                            order['address'] = address_p.text.strip()

                        phone_p = prompt_div.find_all('p')[-1]
                        if phone_p and '****' in phone_p.text:
                            order['phone'] = phone_p.text.strip()

                # 订单金额
                amount_div = tr_bd.find('div', class_='amount')
                if amount_div:
                    amount_span = amount_div.find('span')
                    if amount_span:
                        amount_text = amount_span.text.strip()
                        match = re.search(r'[¥￥]?(\d+\.?\d*)', amount_text)
                        if match:
                            order['amount'] = float(match.group(1))

                    pay_span = amount_div.find('span', class_='ftx-13')
                    if pay_span:
                        order['payment_method'] = pay_span.text.strip()

                # 订单状态
                status_div = tr_bd.find('div', class_='status')
                if status_div:
                    status_span = status_div.find('span', class_='order-status')
                    if status_span:
                        order['status'] = status_span.text.strip()

            return order

        except Exception as e:
            print(f"解析单个订单时出错: {e}")
            return {}

    def crawl(self):
        """
        重写 crawl 方法，支持多页爬取。
        因为京东订单是分页的，我们需要在爬取过程中动态判断是否继续。
        """
        all_orders = []
        current_page = self.start_page

        while True:
            print(f"\n--- 正在获取第 {current_page} 页订单数据 ---")

            # 构造当前页 URL
            url = self.base_url
            # 更新 referer
            headers = self.headers.copy()
            headers["referer"] = f"{self.base_url}?page={max(1, current_page - 1)}"
            params = {
                "page": current_page,
            }

            response = self.make_request(url, headers=headers, cookies=self.cookies,params = params)
            if not response:
                print("请求失败，停止爬取。")
                break

            # 解析当前页
            page_orders = self.parse(response)
            if not page_orders:
                print("当前页无订单数据，可能已爬取完毕。")
                break

            all_orders.extend(page_orders)
            print(f"第 {current_page} 页获取到 {len(page_orders)} 个订单")

            # 检查是否达到结束页
            if self.end_page and current_page >= self.end_page:
                print(f"已达到指定结束页 {self.end_page}")
                break

            current_page += 1
            time.sleep(self.delay)  # 延迟

        # 保存所有数据
        if all_orders:
            print(f"\n🎉 爬取完成！共获取 {len(all_orders)} 个订单。")
            return all_orders

        else:
            print("\n❌ 爬取结束，未获取到任何订单数据。")


# ------------------- 使用示例 -------------------

if __name__ == "__main__":

    # 创建爬虫实例
    spider = JdOrderSpider(
        cookies=cookie,
        start_page=1,
        end_page=1  # 可选：只爬前3页；设为 None 则爬到末页
    )

    # 开始爬取
    spider.crawl()