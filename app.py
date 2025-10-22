import os.path
import sys
from datetime import datetime
from service.login import LoginWindow

from service.storage import cookie
from crawlers.spider import JdOrderSpider
from ui.ui_form import Ui_MainWindow
from PySide6.QtWidgets import *
from PySide6.QtCore import *

from utils.convert import  dict_list_to_2d_array


def load_data_to_table(tableWidget: QTableWidget, data):
    # 设置表格行列数
    tableWidget.setRowCount(len(data))
    tableWidget.setColumnCount(len(data[0]))

    # 加载数据到表格
    for row in range(len(data)):
        for col in range(len(data[row])):
            item = QTableWidgetItem(str(data[row][col]))
            item.setToolTip(item.text())  # 设置提示信息
            tableWidget.setItem(row, col, item)

    # 调整列宽
    tableWidget.resizeColumnsToContents()



def set_table_headers(tableWidget, headers):
    """
    设置 QTableWidget 的表头
    :param tableWidget: QTableWidget 实例
    :param headers: 表头列表（字符串列表）
    """
    # 设置列数为表头数量
    tableWidget.setColumnCount(len(headers))

    # 设置表头
    tableWidget.setHorizontalHeaderLabels(headers)


class DataEntryDialog(QDialog):
    def __init__(self, title, fields, initial_data=None, parent=None):
        super().__init__(parent)
        self.fields = fields
        self.initial_data = initial_data or []
        self.setup_ui(title)

    def setup_ui(self, title):
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # 创建表单
        self.form_layout = QFormLayout()
        self.input_widgets = []

        for i, field in enumerate(self.fields):
            if field == "年龄":  # 年龄使用数字输入框
                input_widget = QSpinBox()
                input_widget.setRange(0, 150)
                input_widget.setValue(
                    int(self.initial_data[i]) if i < len(self.initial_data) and self.initial_data[i] else 0)
            else:  # 其他字段使用文本输入框
                input_widget = QLineEdit()
                input_widget.setText(self.initial_data[i] if i < len(self.initial_data) else "")
                input_widget.setPlaceholderText(f"请输入{field}")

            self.input_widgets.append(input_widget)
            self.form_layout.addRow(f"{field}:", input_widget)

        layout.addLayout(self.form_layout)

        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)
        self.ok_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.cancel_btn.setStyleSheet("background-color: #6c757d; color: white;")

    def get_data(self):
        """获取输入的数据"""
        data = []
        for widget in self.input_widgets:
            if isinstance(widget, QSpinBox):
                data.append(str(widget.value()))
            else:
                data.append(widget.text().strip())
        return data


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 连接登录槽函数
        self.ui.pushButton.clicked.connect(self.login)

        # 连接刷新槽函数
        self.ui.button_flush.clicked.connect(self.button_flush_func)

        # 获取日期
        date = datetime.now().strftime("%Y-%m-%d")
        desktop_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.DesktopLocation),
                                    f"{date}-导出数据.csv")
        # 连接导出槽函数
        self.ui.action.triggered.connect(lambda: self.ui.tableWidget.export_to_csv(desktop_path))

    def login(self):
        self.login_window = LoginWindow("https://order.jd.com/center/list.action")
        self.login_window.show()

    def button_flush_func(self):

        # 创建爬虫实例
        spider = JdOrderSpider(
            cookies=cookie,
            start_page=1,
            end_page=1  # 可选：只爬前3页；设为 None 则爬到末页
        )

        # 开始爬取
        data = spider.crawl()

        # 转换数据
        data = dict_list_to_2d_array(data, exclude_keys=["order_url", "shop_name"])

        # 加载数据到表格
        load_data_to_table(self.ui.tableWidget, data)

    # ---------------------------表格操作方法------------------------


def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
