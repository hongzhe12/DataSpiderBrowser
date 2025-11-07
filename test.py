# simple_resource_manager.py
import os
import subprocess
import importlib.util
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap


class SimpleResourceManager:
    """简化版资源管理器"""

    def __init__(self, qrc_file: str = "resources.qrc"):
        self.qrc_file = qrc_file
        self.output_file = qrc_file.replace('.qrc', '_rc.py')
        self.resources_loaded = False
        self._compile_and_load_resources()

    def _compile_and_load_resources(self):
        """编译并加载资源文件"""
        # 检查是否需要编译
        need_compile = False
        if not os.path.exists(self.output_file):
            need_compile = True
        elif os.path.exists(self.qrc_file):
            # 如果 QRC 文件比编译后的文件新，也需要重新编译
            qrc_mtime = os.path.getmtime(self.qrc_file)
            output_mtime = os.path.getmtime(self.output_file)
            if qrc_mtime > output_mtime:
                need_compile = True

        # 编译资源
        if need_compile and os.path.exists(self.qrc_file):
            try:
                result = subprocess.run([
                    "pyside6-rcc", self.qrc_file, "-o", self.output_file
                ], capture_output=True, text=True, check=True)
                print(f"✅ 资源编译成功: {self.output_file}")
            except subprocess.CalledProcessError as e:
                print(f"❌ 资源编译失败: {e}")
                if e.stderr:
                    print(f"错误信息: {e.stderr}")
                return
            except FileNotFoundError:
                print("❌ 未找到 pyside6-rcc 命令，请确保 PySide6 已正确安装")
                return

        # 加载资源模块
        if os.path.exists(self.output_file):
            try:
                # 使用 importlib 安全地导入模块
                module_name = Path(self.output_file).stem
                spec = importlib.util.spec_from_file_location(module_name, self.output_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.resources_loaded = True
                    print("✅ 资源加载成功")
                else:
                    print("❌ 无法创建模块规范")
            except Exception as e:
                print(f"❌ 资源加载失败: {e}")
        else:
            print(f"❌ 资源文件不存在: {self.output_file}")

    def icon(self, resource_path: str) -> QIcon:
        """获取图标"""
        if not self.resources_loaded:
            print("⚠️ 资源未加载，尝试重新加载...")
            self._compile_and_load_resources()

        icon = QIcon(resource_path)
        if icon.isNull():
            print(f"⚠️ 图标加载失败: {resource_path}")
        return icon

    def pixmap(self, resource_path: str) -> QPixmap:
        """获取图片"""
        if not self.resources_loaded:
            print("⚠️ 资源未加载，尝试重新加载...")
            self._compile_and_load_resources()

        pixmap = QPixmap(resource_path)
        if pixmap.isNull():
            print(f"⚠️ 图片加载失败: {resource_path}")
        return pixmap

    def resource_exists(self, resource_path: str) -> bool:
        """检查资源是否存在"""
        from PySide6.QtCore import QFile
        if not self.resources_loaded:
            self._compile_and_load_resources()
        return QFile(resource_path).exists()


def test_resource_manager():
    """测试资源管理器"""
    print("=== 测试资源管理器 ===")

    # 创建资源管理器
    resource_manager = SimpleResourceManager()

    if not resource_manager.resources_loaded:
        print("❌ 资源管理器初始化失败")
        return False

    # 测试资源路径
    test_paths = [
        ":/icons/jd.svg",
        ":/jd.svg",
        ":/icons/resources/images/jd.svg"
    ]

    success = False
    for path in test_paths:
        print(f"\n测试路径: {path}")

        # 检查资源是否存在
        exists = resource_manager.resource_exists(path)
        print(f"  资源存在: {exists}")

        if exists:
            # 测试图标
            icon = resource_manager.icon(path)
            icon_valid = not icon.isNull()
            print(f"  图标有效: {icon_valid}")

            if icon_valid:
                sizes = icon.availableSizes()
                if sizes:
                    print(f"    可用尺寸: {sizes}")

            # 测试图片
            pixmap = resource_manager.pixmap(path)
            pixmap_valid = not pixmap.isNull()
            print(f"  图片有效: {pixmap_valid}")

            if pixmap_valid:
                print(f"    图片尺寸: {pixmap.width()}x{pixmap.height()}")

            if icon_valid or pixmap_valid:
                success = True
                print(f"✅ 找到可用资源: {path}")
                break

    if success:
        print("\n🎉 资源管理器测试成功！")
    else:
        print("\n💥 资源管理器测试失败")

    return success


# 使用示例
if __name__ == "__main__":
    # 注意：在测试时需要创建 QApplication 实例
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    success = test_resource_manager()

    # 安全退出
    if success:
        sys.exit(0)
    else:
        sys.exit(1)