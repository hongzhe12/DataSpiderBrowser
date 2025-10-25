# 京东订单数据爬取与管理工具

这是一个基于Python开发的图形界面应用程序，用于爬取京东订单数据并在本地进行管理和分析。

## 功能特性

- 🕵️ 自动登录京东并爬取订单数据
- 🖥️ 图形用户界面展示订单详情
- 🔍 多维度订单分类筛选（电脑配件、手机数码、家用电器等）
- 💾 数据导出功能（CSV格式）
- 📤 订单数据分享功能
- 🔄 实时数据刷新

## 技术架构

### 主要组件

- **爬虫模块** (`crawlers/spider.py`)
  - [DebugSpider](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\crawlers\spider.py#L119-L200): 基于 [SimpleSpider](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\crawlers\base_spider.py#L10-L306) 的京东订单爬虫实现
  - [jd_parse_order](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\crawlers\spider.py#L12-L113): 解析京东订单页面HTML结构，提取订单信息
  - 支持自动翻页爬取所有订单数据

- **GUI应用** ([app.py](file://C:\Users\Administrator\PycharmProjects\DataSpiderBrowser\app.py))
  - 基于PySide6的桌面应用程序
  - 提供直观的订单数据展示界面
  - 内置多种筛选和导出功能

### 数据结构

爬取的订单信息包括以下字段：
- 订单编号
- 下单时间
- 商品名称
- 购买数量
- 收货人
- 收货地址
- 联系电话
- 实付金额
- 支付方式
- 订单状态

## 安装指南

### 环境要求
- Python 3.8+
- Windows/Linux/macOS
