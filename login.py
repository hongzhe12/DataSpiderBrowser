import sqlite3
import os
import sys
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QToolBar, QLineEdit,
    QVBoxLayout, QWidget
)
from PySide6.QtWebEngineWidgets import QWebEngineView


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None, main_view=None):
        super().__init__(profile, parent)
        self.profile = profile
        self.main_view = main_view

    def createWindow(self, _type):
        temp_page = QWebEnginePage(self.profile, self)

        def handle_url_changed(url):
            if self.main_view:
                self.main_view.setUrl(url)
            temp_page.deleteLater()

        temp_page.urlChanged.connect(handle_url_changed)
        return temp_page


class BrowserCookies:
    """封装 cookies 操作，方便其他模块调用"""

    def __init__(self, profile_path):
        self.profile_path = profile_path
        self.cookies_db_path = os.path.join(profile_path, "Cookies")

    def get_all_cookies(self):
        """获取所有 cookies"""
        return self._read_cookies_from_db()

    def get_cookies_by_domain(self, domains):
        """
        获取指定域名的 cookies
        :param domains: 字符串或列表，例如 '.ybj.zj.gov.cn' 或 ['paas.ybj.zj.gov.cn', '.ybj.zj.gov.cn']
        """
        if isinstance(domains, str):
            domains = [domains]

        all_cookies = self._read_cookies_from_db()
        return [c for c in all_cookies if any(c['domain'].endswith(domain) for domain in domains)]

    def get_cookies_dict(self, domains=None):
        """
        获取 cookies 字典
        :param domains: 可选，指定域名过滤
        """
        if domains:
            cookies = self.get_cookies_by_domain(domains)
        else:
            cookies = self.get_all_cookies()
        return {c['name']: c['value'] for c in cookies}

    def get_cookie_header(self, domains=None):
        """
        获取 Cookie HTTP 头
        :param domains: 可选，指定域名过滤
        """
        if domains:
            cookies = self.get_cookies_by_domain(domains)
        else:
            cookies = self.get_all_cookies()
        return {'Cookie': '; '.join(f"{c['name']}={c['value']}" for c in cookies)}

    def _read_cookies_from_db(self):
        """从 SQLite 数据库读取 cookies"""
        global conn
        cookies = []
        try:
            conn = sqlite3.connect(self.cookies_db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly 
                FROM cookies
            """)
            for row in cursor.fetchall():
                cookies.append({
                    'domain': row[0],
                    'name': row[1],
                    'value': row[2],
                    'path': row[3],
                    'expires': row[4],
                    'secure': bool(row[5]),
                    'httponly': bool(row[6])
                })
        except Exception as e:
            print(f"读取 cookies 失败: {e}")
        finally:
            conn.close()
        return cookies


class LoginWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()

        # 初始化浏览器配置
        self._init_browser_profile()
        self._init_ui(url)

        # 打印路径信息
        print("实际存储路径:", self.web_engine_profile.persistentStoragePath())
        print("缓存路径:", self.web_engine_profile.cachePath())

        # 初始化 cookies 管理器
        self.cookies_manager = BrowserCookies(self.web_engine_profile.persistentStoragePath())

        # 打印 cookies 示例
        self.print_all_cookies()

    def _init_browser_profile(self):
        """初始化浏览器配置"""
        self.web_engine_profile = QWebEngineProfile("profile", self)
        profile_dir = os.path.abspath(os.path.join(os.getcwd(), "profile"))
        os.makedirs(profile_dir, exist_ok=True)
        self.web_engine_profile.setPersistentStoragePath(profile_dir)
        self.web_engine_profile.setCachePath(profile_dir)
        self.web_engine_profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

    def _init_ui(self, url):
        """初始化用户界面"""
        # 创建浏览器视图
        self.browser = QWebEngineView()
        self.page = CustomWebEnginePage(self.web_engine_profile, self, main_view=self.browser)
        self.browser.setPage(self.page)
        self.browser.setUrl(QUrl(url))

        # 地址栏
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_url_bar)

        # 工具栏
        nav_toolbar = QToolBar("导航")
        self.addToolBar(nav_toolbar)
        self._init_toolbar_actions(nav_toolbar)

        # 主界面布局
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setWindowTitle("简单浏览器")
        self.resize(1024, 768)

    def _init_toolbar_actions(self, toolbar):
        """初始化工具栏按钮"""
        back_btn = QAction("后退", self)
        back_btn.triggered.connect(self.browser.back)
        toolbar.addAction(back_btn)

        forward_btn = QAction("前进", self)
        forward_btn.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_btn)

        reload_btn = QAction("刷新", self)
        reload_btn.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_btn)

        toolbar.addWidget(self.url_bar)

    def navigate_to_url(self):
        """导航到地址栏输入的 URL"""
        url = QUrl(self.url_bar.text())
        if url.scheme() == "":
            url.setScheme("https")
        self.browser.setUrl(url)

    def update_url_bar(self, qurl):
        """更新地址栏显示"""
        self.url_bar.setText(qurl.toString())

    def print_all_cookies(self):
        """打印所有 cookies（示例用法）"""
        cookies = self.cookies_manager.get_all_cookies()
        for cookie in cookies:
            print(f"{cookie['name']}={cookie['value']} (domain: {cookie['domain']})")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow("https://order.jd.com/center/list.action")
    window.show()
    sys.exit(app.exec())


# 使用方法
# from app import BrowserCookies
# cookies_manager = BrowserCookies("profile")
# all_cookies = cookies_manager.get_all_cookies()
# domain_cookies = cookies_manager.get_cookies_by_domain(['.order.jd.com','.jd.com','passport.jd.com'])
# cookies_dict = cookies_manager.get_cookies_dict()
# headers = cookies_manager.get_cookie_header()
# cookies_str = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])