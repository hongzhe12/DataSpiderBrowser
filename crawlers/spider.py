# spider.py

import re

from typing import  Dict, Any

from bs4 import BeautifulSoup

from crawlers.base_spider import SimpleSpider   # 假设 BaseSpider 在 crawlers/base_spider.py



def jd_parse_order(response) -> Dict[str, Any]:
    """从单个订单 tbody 中提取信息（私有方法）"""

    def func(tbody):
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

    soup = BeautifulSoup(response.text, 'html.parser')
    orders = []

    # 查找所有订单的 tbody 元素
    order_tbodies = soup.find_all('tbody', id=re.compile(r'^tb-'))

    for tbody in order_tbodies:
        order = func(tbody)
        if order:
            orders.append(order)
    return orders





class DebugSpider(SimpleSpider):
    """调试用的爬虫，查看实际返回内容"""

    def parse(self, response):
        """
        调试解析方法，查看实际返回内容
        """
        # print(f"\n=== 调试信息 ===")
        # print(f"URL: {response.url}")
        # print(f"状态码: {response.status_code}")
        # print(f"响应头: {dict(response.headers)}")
        # print(f"内容类型: {response.headers.get('Content-Type', 'Unknown')}")
        # print(f"内容长度: {len(response.text)}")
        #
        # # 新增cookies检查
        # print(f"当前会话cookies数量: {len(self.session.cookies)}")
        # print(f"关键cookies: {list(self.session.cookies.keys())}")
        #
        # # 查看前500个字符
        # preview = response.text[:500]
        # print(f"内容预览: {preview}")
        #
        # # 检查是否重定向
        # if response.history:
        #     print(f"重定向历史: {[r.status_code for r in response.history]}")
        #     print(f"最终URL: {response.url}")
        #
        # # 检查是否有错误信息
        # if 'error' in response.text.lower() or 'login' in response.text.lower():
        #     print("⚠️  可能包含错误或登录提示")
        #
        # print("=== 调试结束 ===\n")


        # 返回空数据，因为我们只是调试
        return jd_parse_order(response)

    def before_start(self):
        super().before_start()

        self.session.headers.update({"referer":f"https://order.jd.com/center/list.action?page=1"})

    def crawl_all_pages(self, base_url, **request_kwargs):
        """自动爬取所有页面数据"""
        all_data = []
        page = 1
        while True:
            # 更新参数中的页码
            params = request_kwargs.get('params', {}).copy()
            params['page'] = page
            request_kwargs['params'] = params

            # print(f"正在爬取第 {page} 页...")


            response = self.request(base_url, **request_kwargs)

            if response:
                try:
                    items = self.parse(response)
                    if not items:  # 如果当前页没有数据，说明已经到最后一页
                        print(f"第 {page} 页没有数据，爬取完成")
                        break

                    processed_items = []
                    for item in items:
                        processed_item = self.process_item(item)
                        processed_items.append(processed_item)

                    all_data.extend(processed_items)
                    print(f"从第 {page} 页解析出 {len(processed_items)} 条数据")

                    page += 1

                except Exception as e:
                    print(f"解析第 {page} 页失败: {e}")
                    break
            else:
                print(f"请求第 {page} 页失败，停止爬取")
                break

        return all_data


# 使用示例
if __name__ == "__main__":
    # 使用调试爬虫
    debug_spider = DebugSpider()
    debug_spider.set_headers({
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
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        })
    params = {
        "page": 1,
    }

    data = debug_spider.crawl('https://order.jd.com/center/list.action', method='POST',params = params)
    print(data)