import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from login import LoginWindow
from ui_form import Ui_MainWindow


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.login)

    def login(self):
        self.login_window = LoginWindow("https://order.jd.com/center/list.action")
        self.login_window.show()

def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
