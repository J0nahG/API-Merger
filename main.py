import sys
import os

"""
The following lines are necessary to prevent Uvicorn from crashing when run without a console window.
"""
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import uvicorn
import multiprocessing
from multiprocessing import Process
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListView, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QAbstractListModel
import qdarkstyle
import json
from api import app as api_app


class API():
    """
    Class to handle the subprocess where the localhost API runs.
    """
    def __init__(self):
        """
        Initialize API.
        """
        self.api_process = False

    def api_worker(self):
        """
        Worker that runs the localhost API.
        """
        uvicorn.run(api_app)

    def kill_api(self):
        """
        Terminates the localhost API process.
        """
        if self.api_process:
            self.api_process.terminate()
            self.api_process = False

    def start_api(self):
        """
        Starts the localhost API process.
        """
        if not self.api_process:
            self.api_process = Process(target=self.api_worker, daemon=True)
            self.api_process.start()


class Main_Window(QMainWindow):
    """
    Class for the main application window.
    """

    def __init__(self):
        """
        Initializes the application window.
        """
        super().__init__()
        self.api = API()
        self.setWindowTitle("API Merger")
        self.setGeometry(100, 100, 500, 200)

        self.api_list_model = API_list_model()

        self.api_list_view = QListView(self)
        self.api_list_view.setModel(self.api_list_model)
        self.api_list_view.setGeometry(10, 10, 480, 140)
        self.api_list_view.selectionModel().selectionChanged.connect(self.update_button_state)

        self.start_button = QPushButton("Start API", self)
        self.start_button.setGeometry(10, 160, 100, 30)
        self.start_button.clicked.connect(self.start)

        self.stop_button = QPushButton("Stop API", self)
        self.stop_button.setEnabled(False)
        self.stop_button.setGeometry(120, 160, 100, 30)
        self.stop_button.clicked.connect(self.stop)

        self.add_button = QPushButton("Add New", self)
        self.add_button.setGeometry(230, 160, 100, 30)
        self.add_button.clicked.connect(self.add)

        self.delete_button = QPushButton("Delete", self)
        self.delete_button.setEnabled(False)
        self.delete_button.setGeometry(340, 160, 100, 30)
        self.delete_button.clicked.connect(self.delete)

    def start(self):
        """
        Handles the start button being clicked.
        """
        self.start_button.setEnabled(False)
        self.api.start_api()
        self.stop_button.setEnabled(True)

    def stop(self):
        """
        Handles the stop button being clicked.
        """
        self.stop_button.setEnabled(False)
        self.api.kill_api()
        self.start_button.setEnabled(True)

    def add(self):
        """
        Handles the add button being clicked.
        """
        text, ok = QInputDialog.getText(self, "Input New URL", "Please input the URL you would like to add:")
        if ok:
            if text.startswith('http'):
                self.api_list_model.urls.append(text)
                self.api_list_model.layoutChanged.emit()
                self.api_list_model.update_data()
                if self.api.api_process:
                    self.api.kill_api()
                    self.api.start_api()
            else:
                QMessageBox.information(self, "Error", "Invalid URL! Must begin with 'http' or 'https'", QMessageBox.Ok)

    def delete(self):
        """
        Handles the delete button being clicked.
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            del self.api_list_model.urls[index.row()]
            self.api_list_model.layoutChanged.emit()
            self.api_list_model.update_data()
            self.api_list_view.clearSelection()
            if self.api.api_process:
                self.api.kill_api()
                self.api.start_api()

    def update_button_state(self):
        """
        Updates the state of the delete button (called when selection changes).
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        self.delete_button.setEnabled(bool(selected_indexes))


class API_list_model(QAbstractListModel):
    """
    Class to model the list of URLs.
    """

    def __init__(self):
        """
        Initializes the model.
        """
        super(API_list_model, self).__init__()
        try:
            with open("config.json", 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            self.config = {"urls": []}
            with open("config.json", "w") as config_file:
                json.dump(self.config, config_file)
        self.urls = self.config['urls']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.urls[index.row()].split("?")[0] + "..."

    def rowCount(self, index):
        return len(self.urls)

    def update_data(self):
        """
        Updates config.json to reflect changes in the list of URLs
        """
        self.config["urls"] = self.urls
        with open("config.json", "w") as config_file:
            json.dump(self.config, config_file)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Main_Window()
    window.show()
    sys.exit(app.exec_())
