from PySide6.QtCore import Signal, QObject, Slot


class Worker(QObject):
    """通用工作线程类，用于在后台执行耗时操作"""

    finished = Signal(object)  # 操作完成信号，携带结果
    error = Signal(tuple)  # 错误信号，携带异常类型和异常信息
    progress = Signal(int)  # 进度信号，携带进度值(0-100)

    def __init__(self, func, *args, **kwargs):
        """
        初始化工作线程

        参数:
            func: 要在后台执行的函数
            *args: 传递给函数的位置参数
            **kwargs: 传递给函数的关键字参数
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        # 检查函数是否支持进度回调
        if 'progress_callback' not in self.func.__code__.co_varnames:
            self.kwargs.pop('progress_callback', None)
        else:
            self.kwargs['progress_callback'] = self.progress_callback

    @Slot()
    def run(self):
        """执行工作函数，处理结果和异常"""
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            # 发送错误信号
            self.error.emit((type(e), str(e)))
        else:
            # 发送完成信号和结果
            self.finished.emit(result)

    def progress_callback(self, value):
        """进度回调函数，用于发送进度信号"""
        self.progress.emit(value)
