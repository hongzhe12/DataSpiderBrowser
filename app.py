import os.path
import sys
from datetime import datetime

from PySide6.QtCore import *
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import *

from crawlers.spider import DebugSpider
from service.login import LoginWindow
from ui.ui_form import Ui_MainWindow
from utils.convert import dict_list_to_2d_array
import resources_rc

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
    # tableWidget.resizeColumnsToContents()


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

        self.thread = None

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

        # 连接comboBox的信号
        self.ui.comboBox.currentTextChanged.connect(self.on_combo_box_changed)

        self.ui.share_action.triggered.connect(self.share_order_data)

        self.ui.export_current_page.clicked.connect(self.export_current_page_data)

    def export_current_page_data(self):
        """导出当前页可见的订单数据"""
        # 获取当前页所有可见行的数据
        current_page_data = self.get_current_page_visible_data()

        if not current_page_data:
            QMessageBox.information(self, "提示", "当前页没有可见的订单数据")
            return

        # 格式化分享内容
        share_text = self.format_share_content(current_page_data)

        # 调用系统分享
        self.share_via_system(share_text)

    def get_current_page_visible_data(self):
        """获取当前页所有可见行的数据"""
        table = self.ui.tableWidget
        visible_data = []

        # 获取表头信息
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else f"列 {col}")

        # 遍历所有行，只获取可见行的数据
        for row in range(table.rowCount()):
            if not table.isRowHidden(row):  # 只处理未隐藏的行
                row_data = {}
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    header = headers[col]
                    row_data[header] = item.text() if item else ""
                visible_data.append(row_data)

        return visible_data

    def format_share_content(self, data):
        """格式化分享内容"""
        if not data:
            return ""

        content = "京东订单分享\n\n"
        for order in data:
            content += f"订单号: {order.get('订单编号', '')}\n"
            content += f"商品: {order.get('商品名称', '')}\n"
            content += f"金额: {order.get('实付金额（元）', '')}元\n"
            content += f"时间: {order.get('下单时间', '')}\n"
            content += "-" * 30 + "\n"
        return content

    def on_combo_box_changed(self, text):
        """处理comboBox选择变化"""
        if text == "电脑配件":
            self.filter_computer_accessories()
        elif text == "手机数码":
            self.filter_phone_digital()
        elif text == "家用电器":
            self.filter_home_appliances()
        elif text == "服装鞋帽":
            self.filter_clothing_shoes()
        elif text == "食品饮料":
            self.filter_food_beverage()
        elif text == "美妆个护":
            self.filter_beauty_care()
        elif text == "图书文具":
            self.filter_books_stationery()
        elif text == "运动户外":
            self.filter_sports_outdoor()
        elif text == "家居日用":
            self.filter_home_daily()
        elif text == "母婴玩具":
            self.filter_baby_toys()
        else:
            # 如果选择其他选项，清除筛选
            self.ui.tableWidget.clear_filter()

    def filter_computer_accessories(self):
        """筛选电脑配件订单"""
        computer_keywords = [
            r'电脑|计算机', r'笔记本|台式机', r'CPU|处理器', r'显卡|GPU',
            r'内存|RAM', r'硬盘|固态|SSD|HDD', r'主板|主板芯片', r'电源|电源供应器',
            r'机箱|电脑机箱', r'散热器|风扇|水冷', r'显示器|液晶屏', r'键鼠|键盘|鼠标',
            r'音响|耳机|音箱', r'网卡|路由器|交换机', r'摄像头|麦克风', r'USB|接口|扩展',
            r'光驱|刻录机'
        ]
        pattern = '|'.join(computer_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_phone_digital(self):
        """筛选手机数码订单"""
        phone_keywords = [
            r'手机|智能手机', r'iPhone|安卓', r'平板|iPad', r'智能手表|手环',
            r'耳机|耳麦|蓝牙耳机', r'充电宝|移动电源', r'数据线|充电器', r'手机壳|保护套',
            r'贴膜|屏幕保护膜', r'相机|摄像机|单反', r'镜头|摄影器材', r'自拍杆|三脚架',
            r'存储卡|SD卡|TF卡', r'读卡器|转接头', r'智能家居|智能设备'
        ]
        pattern = '|'.join(phone_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_home_appliances(self):
        """筛选家用电器订单"""
        appliance_keywords = [
            r'电视|电视机|液晶电视', r'冰箱|冷藏柜', r'洗衣机|烘干机', r'空调|空调器',
            r'热水器|电热水器', r'微波炉|烤箱|电磁炉', r'电饭煲|电压力锅', r'吸尘器|扫地机',
            r'电风扇|空气净化器', r'饮水机|净水器', r'榨汁机|料理机', r'电熨斗|挂烫机',
            r'剃须刀|电动牙刷', r'电吹风|美发器', r'加湿器|除湿机'
        ]
        pattern = '|'.join(appliance_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_clothing_shoes(self):
        """筛选服装鞋帽订单"""
        clothing_keywords = [
            r'衬衫|T恤|毛衣', r'外套|夹克|风衣', r'裤子|长裤|短裤', r'裙子|连衣裙',
            r'内衣|内裤|文胸', r'袜子|丝袜', r'运动服|休闲服', r'西装|正装',
            r'羽绒服|棉服', r'泳装|泳衣', r'鞋子|运动鞋', r'皮鞋|凉鞋|拖鞋',
            r'帽子|鸭舌帽', r'围巾|手套', r'皮带|腰带'
        ]
        pattern = '|'.join(clothing_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_food_beverage(self):
        """筛选食品饮料订单"""
        food_keywords = [
            r'零食|小吃|饼干', r'巧克力|糖果', r'坚果|炒货', r'饮料|果汁|矿泉水',
            r'咖啡|茶叶', r'牛奶|酸奶', r'方便面|速食', r'米面|粮油',
            r'调味品|酱油|醋', r'生鲜|水果|蔬菜', r'肉类|海鲜', r'面包|糕点',
            r'酒类|啤酒|白酒', r'保健品|营养品', r'婴儿食品|奶粉'
        ]
        pattern = '|'.join(food_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_beauty_care(self):
        """筛选美妆个护订单"""
        beauty_keywords = [
            r'化妆品|彩妆', r'护肤品|面膜', r'洗面奶|洁面乳', r'香水|香氛',
            r'口红|唇膏', r'眼影|眉笔', r'粉底|BB霜', r'洗发水|护发素',
            r'沐浴露|身体乳', r'牙膏|牙刷', r'剃须|脱毛', r'防晒|隔离',
            r'美容仪|按摩器', r'化妆棉|棉签', r'精油|香薰'
        ]
        pattern = '|'.join(beauty_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_books_stationery(self):
        """筛选图书文具订单"""
        book_keywords = [
            r'图书|书籍', r'小说|文学', r'教材|教辅', r'儿童图书|绘本',
            r'杂志|期刊', r'笔记本|记事本', r'笔|钢笔|圆珠笔', r'文具盒|笔袋',
            r'橡皮|尺子', r'书包|文具包', r'文件袋|文件夹', r'胶水|胶带',
            r'订书机|打孔机', r'计算器|办公用品', r'画材|美术用品'
        ]
        pattern = '|'.join(book_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_sports_outdoor(self):
        """筛选运动户外订单"""
        sports_keywords = [
            r'运动鞋|跑鞋', r'运动服|健身服', r'篮球|足球|排球', r'球拍|网球拍',
            r'健身器材|哑铃', r'瑜伽垫|瑜伽服', r'自行车|骑行', r'帐篷|睡袋',
            r'登山包|户外装备', r'钓鱼|渔具', r'游泳|泳镜', r'滑雪|滑板',
            r'轮滑|溜冰鞋', r'护具|运动保护', r'户外服装|冲锋衣'
        ]
        pattern = '|'.join(sports_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_home_daily(self):
        """筛选家居日用订单"""
        home_keywords = [
            r'家具|沙发|椅子', r'床上用品|床单', r'窗帘|布艺', r'厨具|锅具',
            r'餐具|碗筷', r'清洁用品|洗衣液', r'收纳|整理箱', r'装饰品|摆件',
            r'灯具|台灯', r'地毯|地垫', r'钟表|闹钟', r'镜子|梳妆台',
            r'毛巾|浴巾', r'雨伞|雨具', r'家居服|拖鞋'
        ]
        pattern = '|'.join(home_keywords)
        self._apply_filter_by_product_name(pattern)

    def filter_baby_toys(self):
        """筛选母婴玩具订单"""
        baby_keywords = [
            r'婴儿服装|童装', r'尿不湿|纸尿裤', r'奶粉|奶瓶', r'婴儿车|婴儿床',
            r'玩具|积木', r'娃娃|玩偶', r'模型|拼装', r'电动玩具|遥控',
            r'益智玩具|早教', r'滑板车|自行车', r'婴儿食品|辅食', r'孕产妇用品',
            r'儿童座椅|安全', r'洗护用品|婴儿', r'书包|文具'
        ]
        pattern = '|'.join(baby_keywords)
        self._apply_filter_by_product_name(pattern)

    def _apply_filter_by_product_name(self, pattern):
        """通用的按商品名称筛选方法"""
        # 查找商品名称列
        product_column = self._find_product_name_column()

        # 应用筛选
        if product_column != -1:
            self.ui.tableWidget.apply_filter(product_column, pattern, "regex")
        else:
            # 如果没找到商品名称列，则筛选所有列
            self.ui.tableWidget.apply_filter(-1, pattern, "regex")

    def _find_product_name_column(self):
        """查找商品名称列的索引"""
        for col in range(self.ui.tableWidget.columnCount()):
            header_item = self.ui.tableWidget.horizontalHeaderItem(col)
            if header_item:
                header_text = header_item.text()
                if any(keyword in header_text for keyword in ['商品名称', '产品名称', '品名', '名称']):
                    return col
        return -1

    def login(self):
        self.login_window = LoginWindow("https://order.jd.com/center/list.action")
        self.login_window.show()



    def button_flush_func(self):
        '''
        刷新数据
        '''


        data = self.crawl_jd_orders()
        # 转换数据
        data = dict_list_to_2d_array(data, exclude_keys=["order_url", "shop_name", "product_url"])

        # 加载数据到表格
        load_data_to_table(self.ui.tableWidget, data)
        header = ['订单编号', '下单时间', '商品名称', '购买数量', '收货人', '收货地址', '联系电话', '实付金额（元）',
                  '支付方式', '订单状态']
        self.ui.tableWidget.setHorizontalHeaderLabels(header)

        self.statusBar().showMessage("京东订单爬取完成", 3000)



    def crawl_jd_orders(self):
        """执行京东订单爬取的实际函数"""
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

        base_url = 'https://order.jd.com/center/list.action'
        params = {"page": 1}

        # 使用支持进度回调的版本
        data = debug_spider.crawl_all_pages(base_url, method='POST', params=params)
        return data

    def share_order_data(self):
        """分享订单数据"""
        # 获取选中的订单数据
        selected_data = self.ui.tableWidget.get_selected_data()

        if not selected_data:
            QMessageBox.warning(self, "警告", "请先选择要分享的订单数据")
            return

        # 格式化分享内容
        share_text = self.format_share_content(selected_data)

        # 显示分享选项对话框
        self.show_share_dialog(share_text)

    def format_share_content(self, data):
        """格式化分享内容"""
        content = "京东订单分享\n\n"
        for order in data:
            content += f"订单号: {order.get('订单编号', '')}\n"
            content += f"商品: {order.get('商品名称', '')}\n"
            content += f"金额: {order.get('实付金额（元）', '')}元\n"
            content += f"时间: {order.get('下单时间', '')}\n"
            content += "-" * 30 + "\n"
        return content

    def show_share_dialog(self, content):
        """显示分享选项对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("分享订单")
        dialog.resize(300, 200)

        layout = QVBoxLayout(dialog)

        label = QLabel("选择分享方式:")
        layout.addWidget(label)


        # 系统分享按钮
        system_btn = QPushButton("系统分享")

        system_btn.clicked.connect(lambda: self.share_via_system(content))
        layout.addWidget(system_btn)

        dialog.exec()


    def share_via_system(self, content):
        """通过系统分享"""
        # 创建临时文本文件并使用系统分享
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_file = f.name

        # 使用系统默认方式打开分享
        QDesktopServices.openUrl(QUrl.fromLocalFile(temp_file))


def main():
    try:
        from ctypes import windll
        myappid = 'mycompany.myproduct.subproduct.version'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./resources/images/京东.svg"))
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
