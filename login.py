import os
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QToolBar, QLineEdit,
    QVBoxLayout, QWidget
)


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

        self.conn  = None


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

    def get_cookie(self):
        """打印所有 cookies（示例用法）"""
        cookie = self.cookies_manager.get_cookies_dict()
        return  cookie


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow("https://order.jd.com/center/list.action")
    window.show()
    sys.exit(app.exec())