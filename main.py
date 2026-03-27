import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enterprise-Grade Recruitment CRM + ATS')
        self.setGeometry(100, 100, 800, 600)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

# Developed by abhilashbhosale - GitHub Profile: https://github.com/abhilashbhosale