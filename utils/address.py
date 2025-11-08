import re


def desensitize_address(address):
    """
    对地址进行脱敏处理，仅保留省份或城市
    :param address: 原始地址
    :return: 脱敏后的地址
    """
    if not address:
        return ""

    # 常见的直辖市
    municipalities = ['北京市', '上海市', '天津市', '重庆市']

    # 检查是否是直辖市
    for municipality in municipalities:
        if municipality in address:
            return municipality

    # 匹配省份
    province_patterns = [
        r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼]{1,2}(?:省|市|自治区))',
        r'(内蒙古自治区|广西壮族自治区|西藏自治区|宁夏回族自治区|新疆维吾尔自治区)'
    ]

    for pattern in province_patterns:
        match = re.search(pattern, address)
        if match:
            return match.group(1)

    # 匹配地级市
    city_pattern = r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼]{1,2}[\u4e00-\u9fa5]{1,3}市)'
    city_match = re.search(city_pattern, address)
    if city_match:
        return city_match.group(1)

    # 如果以上都不匹配，返回前6个字符加脱敏标记
    return address[:6] + "****"


def desensitize_consignee(name):
    """
    对收货人姓名进行脱敏处理，保留姓氏，名字用星号替代
    :param name: 原始姓名
    :return: 脱敏后的姓名
    """
    if not name:
        return ""

    # 如果姓名只有一个字符，直接返回星号
    if len(name) == 1:
        return "*"

    # 保留第一个字符（姓氏），其余用星号替代
    return name[0] + "*" * (len(name) - 1)
