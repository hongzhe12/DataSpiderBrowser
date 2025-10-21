import re
from typing import List

from bs4 import BeautifulSoup
def parse_jd_orders_html(html_content)-> List[dict]:
    """
    解析京东订单页面的HTML内容，提取订单信息
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    orders = []

    # 查找所有订单的tbody元素
    order_tbodies = soup.find_all('tbody', id=re.compile(r'^tb-'))

    for tbody in order_tbodies:
        order = extract_order_info(tbody)
        if order:
            orders.append(order)

    return orders


def extract_order_info(tbody) -> dict:
    """
    从单个订单tbody中提取订单信息
    """
    try:
        order = {}

        # 提取订单基本信息
        tr_th = tbody.find('tr', class_='tr-th')
        if not tr_th:
            return None

        # 订单号
        order_link = tr_th.find('a', {'name': 'orderIdLinks'})
        if order_link:
            order['order_id'] = order_link.text.strip()
            order['order_url'] = order_link.get('href', '')

        # 订单时间
        dealtime_span = tr_th.find('span', class_='dealtime')
        if dealtime_span:
            order['order_time'] = dealtime_span.get('title', '').strip()

        # 店铺信息
        shop_span = tr_th.find('span', class_='order-shop')
        if shop_span:
            shop_link = shop_span.find('a', class_='shop-txt')
            if shop_link:
                order['shop_name'] = shop_link.text.strip()

        # 提取商品信息
        tr_bd = tbody.find('tr', class_='tr-bd')
        if tr_bd:
            # 商品信息
            goods_item = tr_bd.find('div', class_='goods-item')
            if goods_item:
                # 商品图片
                img = goods_item.find('img')
                if img:
                    order['product_image'] = img.get('data-lazy-img', '')

                # 商品名称
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

        # 收货人信息
        consignee_div = tr_bd.find('div', class_='consignee')
        if consignee_div:
            consignee_span = consignee_div.find('span', class_='txt')
            if consignee_span:
                order['consignee'] = consignee_span.text.strip()

            # 详细地址信息（在tooltip中）
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
                # 提取金额数字
                match = re.search(r'[¥￥]?(\d+\.?\d*)', amount_text)
                if match:
                    order['amount'] = float(match.group(1))

            # 支付方式
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
        print(f"解析订单信息时出错: {e}")
        return None


def get_jd_orders(cookies, start_page=1, end_page=None, delay=1):
    """
    获取京东订单信息（支持获取多页数据）

    参数:
        cookies: 登录后的cookie字典，用于身份验证
        start_page: 起始页码，默认为1
        end_page: 结束页码，如果为None则获取到最后一页
        delay: 请求间隔时间（秒），避免请求过快，默认为1秒

    返回:
        解析后的订单信息列表
    """
    import requests
    import time

    all_orders = []
    current_page = start_page

    while True:
        print(f"正在获取第 {current_page} 页订单数据...")

        url = "https://order.jd.com/center/list.action"

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",  # 修改为same-origin
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "referer": f"https://order.jd.com/center/list.action?page={max(1, current_page - 1)}"  # 添加referer
        }

        params = {
            "page": current_page,
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                params=params,
                timeout=10
            )

            # 检查请求是否成功
            if response.status_code != 200:
                print(f"第 {current_page} 页请求失败，状态码: {response.status_code}")
                break

            # 检查页面内容是否有效
            if "订单" not in response.text and current_page > 1:
                print(f"第 {current_page} 页无数据，已获取所有订单")
                break

            # 解析当前页订单
            page_orders = parse_jd_orders_html(response.text)

            if not page_orders:
                print(f"第 {current_page} 页没有订单数据")
                break

            all_orders.extend(page_orders)
            print(f"第 {current_page} 页获取到 {len(page_orders)} 个订单")

            # 检查是否达到结束页码
            if end_page and current_page >= end_page:
                print(f"已达到指定结束页码 {end_page}")
                break

            current_page += 1

            # 添加延迟，避免请求过快
            if delay > 0:
                time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"第 {current_page} 页请求异常: {e}")
            break
        except Exception as e:
            print(f"第 {current_page} 页处理异常: {e}")
            break

    print(f"共获取 {len(all_orders)} 个订单，从第 {start_page} 页到第 {current_page - 1} 页")
    return all_orders


def jd_orders_to_table_data(orders: List[dict]) -> List[List]:
    """
    将京东订单数据转换为表格数据格式
    """
    if not orders:
        return []

    # 定义表头（可以根据需要调整）
    headers = [
        "订单号", "订单时间", "商品名称", "数量",
        "收货人", "地址", "金额", "状态", "支付方式"
    ]

    data = [headers]  # 第一行是表头

    for order in orders:
        row = [
            order.get('order_id', ''),
            order.get('order_time', ''),
            order.get('product_name', ''),
            str(order.get('quantity', 0)),
            order.get('consignee', ''),
            order.get('address', ''),
            f"¥{order.get('amount', 0)}",
            order.get('status', ''),
            order.get('payment_method', '')
        ]
        data.append(row)

    return data