import time
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin
import requests

from service.storage import cookie


class SimpleSpider(ABC):
    """
    简单易用的爬虫基类
    技术细节完全封装，开发者只需关注解析逻辑
    """

    def __init__(self,
                 name: str = None,
                 delay: float = 0,
                 timeout: float = 30.0,
                 retry_times: int = 3):
        """
        初始化爬虫

        Args:
            name: 爬虫名称，默认使用类名
            delay: 请求延迟，避免过于频繁
            timeout: 请求超时时间
            retry_times: 失败重试次数
        """
        self.name = name or self.__class__.__name__
        self.delay = delay
        self.timeout = timeout
        self.retry_times = retry_times

        # 创建会话
        self.session = requests.Session()
        self._setup_session()

        # 统计信息
        self.stats = {
            'total_requests': 0,
            'success_requests': 0,
            'failed_requests': 0,
            'total_data': 0,
            'start_time': None,
            'end_time': None
        }
        self.set_cookies(cookie)

    def _setup_session(self):
        """设置默认会话配置"""
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(default_headers)

    def set_headers(self, headers: Dict[str, str]):
        """设置请求头"""
        self.session.headers.update(headers)

    def set_cookies(self, cookies: Dict[str, str]):
        """设置Cookies"""
        self.session.cookies.update(cookies)

    def set_proxies(self, proxies: Dict[str, str]):
        """设置代理"""
        self.session.proxies.update(proxies)

    def request(self,
                url: str,
                method: str = 'GET',
                params: Dict = None,
                data: Dict = None,
                json_data: Dict = None,
                headers: Dict = None,
                **kwargs) -> Optional[requests.Response]:
        """
        执行HTTP请求

        Args:
            url: 请求URL
            method: 请求方法 GET/POST/PUT/DELETE
            params: URL查询参数
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            **kwargs: 其他requests参数

        Returns:
            Response对象或None
        """
        # 请求配置
        request_kwargs = {
            'timeout': self.timeout,
            'headers': headers or {},
        }

        # 添加参数
        if params:
            request_kwargs['params'] = params
        if data:
            request_kwargs['data'] = data
        if json_data:
            request_kwargs['json'] = json_data

        request_kwargs.update(kwargs)

        # 重试机制
        for attempt in range(self.retry_times):
            try:
                self.stats['total_requests'] += 1

                # 请求延迟
                if self.delay > 0 and self.stats['total_requests'] > 1:
                    time.sleep(self.delay)

                print(f"[{self.name}] {method} {url}")

                # 执行请求
                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    **request_kwargs
                )

                # 检查状态码
                if response.status_code == 200:
                    self.stats['success_requests'] += 1
                    return response
                else:
                    print(f"[{self.name}] 请求失败: {response.status_code}")

            except requests.RequestException as e:
                print(f"[{self.name}] 请求异常 (尝试 {attempt + 1}/{self.retry_times}): {e}")

            except Exception as e:
                print(f"[{self.name}] 未知错误: {e}")
                break

        self.stats['failed_requests'] += 1
        return None

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """GET请求快捷方法"""
        return self.request(url, 'GET', **kwargs)

    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """POST请求快捷方法"""
        return self.request(url, 'POST', **kwargs)

    def download_file(self, url: str, filepath: str, **kwargs) -> bool:
        """
        下载文件

        Args:
            url: 文件URL
            filepath: 保存路径
            **kwargs: 请求参数

        Returns:
            是否下载成功
        """
        response = self.get(url, **kwargs)
        if response and response.status_code == 200:
            try:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"[{self.name}] 文件下载成功: {filepath}")
                return True
            except Exception as e:
                print(f"[{self.name}] 文件保存失败: {e}")
        return False

    def build_url(self, base_url: str, **path_params) -> str:
        """
        构建URL，支持路径参数

        Args:
            base_url: 基础URL，可包含 {param} 占位符
            **path_params: 路径参数

        Returns:
            构建后的URL
        """
        if path_params:
            return base_url.format(**path_params)
        return base_url

    @abstractmethod
    def parse(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        解析响应内容 - 必须实现的方法

        Args:
            response: 响应对象

        Returns:
            数据列表，每个字典是一条数据记录
        """
        pass

    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单条数据 - 可选重写

        Args:
            item: 原始数据项

        Returns:
            处理后的数据项
        """
        return item

    def save_data(self, data: List[Dict[str, Any]]):
        """
        保存数据 - 可选重写

        Args:
            data: 数据列表
        """
        if not data:
            return

        # 默认保存为JSON文件
        filename = f"{self.name}_{int(time.time())}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[{self.name}] 数据已保存到: {filename}")
        except Exception as e:
            print(f"[{self.name}] 数据保存失败: {e}")

    def before_start(self):
        """爬取开始前的准备工作 - 可选重写"""
        print(f"[{self.name}] 开始爬取...")
        self.stats['start_time'] = time.time()

    def after_finish(self, data: List[Dict[str, Any]]):
        """爬取结束后的清理工作 - 可选重写"""
        self.stats['end_time'] = time.time()
        self.stats['total_data'] = len(data)

        duration = self.stats['end_time'] - self.stats['start_time']
        print(f"[{self.name}] 爬取完成!")
        print(f"[{self.name}] 统计信息:")
        print(f"  - 总请求数: {self.stats['total_requests']}")
        print(f"  - 成功请求: {self.stats['success_requests']}")
        print(f"  - 失败请求: {self.stats['failed_requests']}")
        print(f"  - 获取数据: {self.stats['total_data']} 条")
        print(f"  - 耗时: {duration:.2f} 秒")

    def crawl(self, urls: Union[str, List[str]], **request_kwargs) -> List[Dict[str, Any]]:
        """
        执行爬取任务

        Args:
            urls: 要爬取的URL或URL列表
            **request_kwargs: 请求参数

        Returns:
            爬取到的所有数据
        """
        # 准备阶段
        self.before_start()

        # 统一URL格式
        if isinstance(urls, str):
            urls = [urls]

        all_data = []

        # 遍历URL进行爬取
        for url in urls:
            response = self.request(url, **request_kwargs)

            if response:
                try:
                    # 解析数据
                    items = self.parse(response)

                    # 处理数据
                    processed_items = []
                    for item in items:
                        processed_item = self.process_item(item)
                        processed_items.append(processed_item)

                    all_data.extend(processed_items)
                    print(f"[{self.name}] 从 {url} 解析出 {len(processed_items)} 条数据")

                except Exception as e:
                    print(f"[{self.name}] 解析失败 {url}: {e}")
            else:
                print(f"[{self.name}] 请求失败: {url}")

        # 保存数据
        self.save_data(all_data)

        # 结束阶段
        self.after_finish(all_data)

        return all_data