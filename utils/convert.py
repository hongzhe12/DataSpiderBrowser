from typing import List, Dict, Any, Callable, Optional

from typing import List, Dict, Any


from typing import List, Dict, Any, Optional

def dict_list_to_2d_array(
    data: List[Dict[str, Any]],
    exclude_keys: Optional[List[str]] = None,
    keys: Optional[List[str]] = None
) -> List[List[Any]]:
    """
    将字典列表转换为二维列表，支持排除指定列。

    Args:
        data: 字典列表
        exclude_keys: 要排除的字段名列表，如 ['phone', 'address']
        keys: 明确指定保留的字段顺序。若提供，则 exclude_keys 无效。

    Returns:
        二维列表，每行对应一个字典的值（已过滤指定列）
    """
    if not data:
        return []

    # 如果明确指定了 keys，直接使用
    if keys is not None:
        pass
    # 否则使用第一个字典的键，并排除 exclude_keys 中的列
    elif exclude_keys is not None:
        keys = [k for k in data[0].keys() if k not in exclude_keys]
    else:
        keys = list(data[0].keys())

    return [[item.get(k) for k in keys] for item in data]


# ------------------- 使用示例 -------------------

if __name__ == "__main__":
    # 模拟京东订单数据
    jd_orders = [
        {
            'order_id': 'JD123456789',
            'order_time': '2025-10-20 10:30:00',
            'product_name': 'iPhone 15',
            'quantity': 1,
            'consignee': '张三',
            'address': '北京市朝阳区xxx街道',
            'amount': 5999,
            'status': '已签收',
            'payment_method': '在线支付'
        },
        {
            'order_id': 'JD987654321',
            'order_time': '2025-10-19 15:20:00',
            'product_name': 'MacBook Pro',
            'quantity': 1,
            'consignee': '李四',
            'address': '上海市浦东新区xxx路',
            'amount': 15999,
            'status': '运输中',
            'payment_method': '货到付款'
        }
    ]

    # 转换为表格数据
    table_data = dict_list_to_2d_array(jd_orders)

    # 打印结果
    for row in table_data:
        print(row)