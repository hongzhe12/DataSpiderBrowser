import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class StyledTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_table_operations()

        # 添加筛选功能相关属性
        self.filter_active = False
        self.filtered_rows = set()

    def apply_filter(self, column, pattern, match_type="contains"):
        """应用筛选条件
        Args:
            column: 要筛选的列索引，-1表示所有列
            pattern: 筛选模式
            match_type: 匹配类型 ("contains", "equals", "regex")
        """
        if not pattern:
            return

        self.filter_active = True
        self.filtered_rows.clear()

        try:
            import re
            for row in range(self.rowCount()):
                show_row = False

                if column == -1:  # 所有列
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        if item and self._match_item(item.text(), pattern, match_type):
                            show_row = True
                            break
                else:  # 特定列
                    item = self.item(row, column)
                    if item and self._match_item(item.text(), pattern, match_type):
                        show_row = True

                # 根据匹配结果隐藏或显示行
                self.setRowHidden(row, not show_row)
                if not show_row:
                    self.filtered_rows.add(row)

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "筛选错误", f"筛选过程中发生错误: {str(e)}")

    def _match_item(self, text, pattern, match_type):
        """匹配单个单元格文本"""
        try:
            if match_type == "contains":
                return pattern.lower() in text.lower()
            elif match_type == "equals":
                return text.lower() == pattern.lower()
            elif match_type == "regex":
                import re
                return bool(re.search(pattern, text, re.IGNORECASE))
        except Exception:
            return False
        return False

    def clear_filter(self):
        """清除筛选，显示所有行"""
        self.filter_active = False
        self.filtered_rows.clear()

        # 显示所有行
        for row in range(self.rowCount()):
            self.setRowHidden(row, False)

    def setup_ui(self):
        # 你现有的UI设置代码
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

        font = QFont("Segoe UI", 10)
        self.setFont(font)

        header_font = QFont("Segoe UI", 10, QFont.Bold)
        self.horizontalHeader().setFont(header_font)

    def setup_table_operations(self):
        """设置表格操作功能"""
        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # 启用拖拽
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)

        # 添加操作
        # 只在有选中行时显示删除选项
        if self.selectedRanges():
            delete_row_action = menu.addAction("删除选中行")
            delete_row_action.triggered.connect(self.delete_selected_row)
            delete_row_action.triggered.connect(self.delete_selected_row)

        # add_row_action = menu.addAction("添加行")
        clear_action = menu.addAction("清空表格")

        # 连接信号
        # add_row_action.triggered.connect(self.add_row)
        clear_action.triggered.connect(self.clear_table)

        menu.exec_(self.mapToGlobal(position))

    def add_row(self):
        """在末尾添加新行"""
        row_position = self.rowCount()
        self.insertRow(row_position)

    def delete_selected_row(self):
        """删除所有选中的行"""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        # 获取所有要删除的行索引（从大到小排序，避免删除时索引变化）
        rows_to_delete = set()
        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                rows_to_delete.add(row)

        # 从大到小排序，这样删除时不会影响前面的索引
        rows_to_delete = sorted(rows_to_delete, reverse=True)

        # 删除所有选中的行
        for row in rows_to_delete:
            self.removeRow(row)

    def clear_table(self):
        """清空表格"""
        self.setRowCount(0)

    def get_selected_data(self):
        """获取所有选中行的数据"""
        selected_ranges = self.selectedRanges()

        if not selected_ranges:
            return []

        data_list = []
        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                row_data = {}
                for col in range(self.columnCount()):
                    item = self.item(row, col)
                    if item:
                        header = self.horizontalHeaderItem(col)
                        row_data[header.text() if header else f"Column {col}"] = item.text()
                data_list.append(row_data)

        return data_list

    def set_column_headers(self, headers):
        """设置表头"""
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def add_row_data(self, data):
        """添加一行数据"""
        row = self.rowCount()
        self.insertRow(row)
        for col, value in enumerate(data):
            self.setItem(row, col, QTableWidgetItem(str(value)))

    def export_to_csv(self, filename, export_selected_only=True):
        """导出到CSV文件
        Args:
            filename: 导出文件名
            export_selected_only: 是否只导出选中行，False则导出所有行
        """
        print(f"导出路径:{filename}")
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                # 写入表头
                # headers = []
                # for col in range(self.columnCount()):
                #     header = self.horizontalHeaderItem(col)
                #     headers.append(header.text() if header else f"Column {col}")
                # file.write(','.join(headers) + '\n')

                # 确定要导出的行范围
                if export_selected_only:
                    # 只导出选中行
                    selected_ranges = self.selectedRanges()
                    if not selected_ranges:
                        print("没有选中的行可导出")
                        return False

                    rows_to_export = set()
                    for selected_range in selected_ranges:
                        for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                            rows_to_export.add(row)
                    rows_to_export = sorted(rows_to_export)
                else:
                    # 导出所有行
                    rows_to_export = range(self.rowCount())

                # 写入数据
                export_count = 0
                for row in rows_to_export:
                    row_data = []
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        # 处理包含逗号的内容，用引号包围
                        text = item.text() if item else ""
                        if ',' in text:
                            text = f'"{text}"'
                        row_data.append(text)
                    file.write(','.join(row_data) + '\n')
                    export_count += 1

                print(f"成功导出 {export_count} 行数据")
                return True

        except Exception as e:
            print(f"导出失败: {e}")
            return False
