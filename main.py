import sys
import os

"""
The following lines are necessary to prevent Uvicorn from crashing when run without a console window.
"""
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import multiprocessing
from PyQt5.QtWidgets import QApplication
import qdarkstyle
from src.main_window import Main_Window



if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Main_Window()
    window.show()
    sys.exit(app.exec_())
