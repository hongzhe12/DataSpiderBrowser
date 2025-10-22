from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time


class BaseSpider(ABC):
    """
    爬虫抽象基类，定义了爬虫必须实现的核心方法。
    子类需要实现具体的请求、解析和数据处理逻辑。
    """

    def __init__(self, name: str, start_urls: List[str], delay: float = 1.0):
        """
        初始化爬虫。

        Args:
            name (str): 爬虫名称
            start_urls (List[str]): 起始 URL 列表
            delay (float): 请求间隔时间（秒），防止请求过于频繁
        """
        self.name = name
        self.start_urls = start_urls
        self.delay = delay
        self.session = requests.Session()
        # 可在此处设置默认 headers
        self.session.headers.update({
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
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        })

    @abstractmethod
    def start_requests(self) -> List[str]:
        """
        必须实现：返回起始请求的 URL 列表。
        通常直接返回 self.start_urls，也可在此方法中生成动态起始 URL。

        Returns:
            List[str]: 起始 URL 列表
        """
        pass

    @abstractmethod
    def parse(self, response: requests.Response, **kwargs) -> List[Dict[str, Any]]:
        """
        必须实现：解析响应内容，提取数据和/或新的请求 URL。
        这是爬虫的核心逻辑，子类需要根据目标网页结构进行实现。

        Args:
            response (requests.Response): HTTP 响应对象
            **kwargs: 可传递额外的上下文信息

        Returns:
            List[Dict[str, Any]]: 解析得到的数据列表，每个字典代表一条数据记录
        """
        pass

    @abstractmethod
    def get_data(self, data: List[Dict[str, Any]]):
        """
        必须实现：将提取的数据保存到文件或数据库。
        具体保存方式（如 CSV、JSON、数据库）由子类决定。

        Args:
            data (List[Dict[str, Any]]): 要保存的数据列表
            filename (str): 保存文件的路径或名称
        """
        pass

    def make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        执行 HTTP 请求，包含异常处理和请求间隔控制。
        可被子类重写以支持更复杂的请求逻辑（如使用代理、重试机制）。

        Args:
            url (str): 请求的 URL
            **kwargs: 传递给 requests.get() 的额外参数

        Returns:
            Optional[requests.Response]: 响应对象，请求失败时返回 None
        """
        try:
            print(f"正在请求: {url}")
            time.sleep(self.delay)  # 遵守爬虫礼仪，添加延迟
            response = self.session.get(url, **kwargs)
            response.raise_for_status()  # 检查 HTTP 错误状态
            return response
        except requests.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None

    def is_valid_url(self, url: str, allowed_domains: List[str]) -> bool:
        """
        检查 URL 是否属于允许的域名，用于限制爬取范围。
        可被子类重写以实现更复杂的 URL 过滤逻辑。

        Args:
            url (str): 待检查的 URL
            allowed_domains (List[str]): 允许的域名列表

        Returns:
            bool: URL 是否有效
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            return any(allowed_domain in domain for allowed_domain in allowed_domains)
        except Exception:
            return False

    def crawl(self):
        """
        爬虫的主运行方法，定义了爬取的整体流程。
        1. 获取起始 URL
        2. 对每个 URL 发起请求
        3. 解析响应内容
        4. 保存数据
        """
        urls = self.start_requests()
        all_data = []

        for url in urls:

            response = self.make_request(url)
            if response:
                try:
                    data = self.parse(response)
                    all_data.extend(data)
                    print(f"成功解析 {len(data)} 条数据来自 {url}")
                except Exception as e:
                    print(f"解析失败 {url}: {e}")
            else:
                print(f"跳过无法请求的 URL: {url}")

        if all_data:
            filename = f"{self.name}_data.json"
            self.get_data(all_data, filename)
            print(f"爬取完成，共获取 {len(all_data)} 条数据，已保存至 {filename}")
        else:
            print("爬取结束，未获取到有效数据。")