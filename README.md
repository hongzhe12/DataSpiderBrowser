# DataSpiderBrowser 项目 README

## 📋 项目概述

DataSpiderBrowser 是一个通用的桌面爬虫应用程序，它结合了嵌入式浏览器、网络爬虫框架和数据展示功能。虽然当前实现了京东订单爬虫作为示例，但它被设计为支持多种网站的数据抓取。

### 主要特性：

- 内置浏览器用于用户登录和认证
- 自动保存登录 cookies 供后续爬虫使用
- 可扩展的通用爬虫框架
- 数据可视化展示在表格中
- 支持导出数据为 CSV 文件
- 模块化设计，易于添加新的爬虫实现

## 🛠️ 技术栈

- Python 3.x
- PySide6 (Qt for Python)
- Requests
- BeautifulSoup4
- SQLite3

## 📁 项目结构

```
DataSpiderBrowser/
├── app.py              # 主应用程序入口
├── crawlers/           # 爬虫相关模块
│   ├── base_spider.py  # 爬虫抽象基类
│   └── spider.py       # 具体爬虫实现（以京东订单为例）
├── service/            # 服务层
│   ├── login.py        # 浏览器登录窗口
│   └── storage.py      # 数据存储相关
├── ui/                 # 用户界面
│   └── ui_form.py      # 主窗口UI定义
├── utils/              # 工具函数
│   └── convert.py      # 数据转换工具
├── widget/             # 自定义控件
│   └── styledtablewidget.py  # 自定义表格控件
└── profile/            # 浏览器配置和cookies存储目录
```


## 🚀 安装与运行

### 安装依赖

```bash
pip install PySide6 requests beautifulsoup4
```


### 运行程序

```bash
python app.py
```


## 🧭 使用说明

1. **登录网站**
   - 点击"登录"按钮打开内置浏览器
   - 在浏览器中登录目标网站
   - 登录成功后关闭浏览器窗口

2. **抓取数据**
   - 点击"刷新"按钮开始抓取数据
   - 数据会自动显示在下方表格中

3. **导出数据**
   - 点击"文件"菜单中的"导出"选项
   - 数据将导出为 CSV 文件保存到桌面

## ⚙️ 核心组件介绍

### [BaseSpider](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\crawlers\base_spider.py#L7-L152) (crawlers/base_spider.py)
爬虫抽象基类，定义了通用爬虫框架：
- HTTP 请求管理
- 延迟控制防反爬
- URL 过滤机制
- 统一的数据处理流程

### [StyledTableWidget](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\widget\styledtablewidget.py#L6-L169) (widget/styledtablewidget.py)
自定义表格控件，具有以下功能：
- 美观的样式设计
- 右键菜单支持（删除行、清空表格）
- 数据导出为 CSV 功能
- 表格操作功能

### [LoginWindow](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\service\login.py#L41-L124) (service/login.py)
内置浏览器窗口：
- 基于 Qt WebEngine
- 支持持久化 cookies 存储
- 可以处理新窗口请求

### [dict_list_to_2d_array](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\utils\convert.py#L9-L36) (utils/convert.py)
数据转换工具：
- 将字典列表转换为二维数组
- 支持字段筛选和排序

## 🔧 扩展新的爬虫

要添加新的网站爬虫：

1. 继承 [BaseSpider](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\crawlers\base_spider.py#L7-L152) 类
2. 实现 `start_requests`、`parse` 和 `get_data` 抽象方法
3. 在主应用中集成新的爬虫逻辑

## 🔒 注意事项

1. 本工具仅供学习交流使用，请遵守相关法律法规和网站使用条款
2. 不要频繁请求目标服务器，以免对网站造成压力
3. 个人信息和 cookies 会保存在本地，请注意数据安全

## 📤 导出功能

- 支持导出所有数据或仅选中行数据
- 导出文件为 CSV 格式
- 默认保存到桌面，文件名为 "YYYY-MM-DD-导出数据.csv"

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📄 许可证

该项目基于 MIT 许可证开源。