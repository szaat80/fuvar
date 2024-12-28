import sys
from PySide6.QtWidgets import QApplication
from modified_main import FuvarAdminApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FuvarAdminApp()
    window.show()
    sys.exit(app.exec())