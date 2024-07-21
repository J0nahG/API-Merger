import json
from PyQt5.QtWidgets import QMainWindow, QListView, QPushButton, QMenu, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QAbstractListModel
from .api_handler import API_Handler


class Main_Window(QMainWindow):
    """
    Class for the main application window.
    """

    def __init__(self):
        """
        Initializes the application window.
        """
        super().__init__()
        self.api = API_Handler()
        self.setWindowTitle("API Merger")
        self.setGeometry(100, 100, 560, 200)

        self.api_list_model = API_list_model(self.api)

        self.api_list_view = QListView(self)
        self.api_list_view.setModel(self.api_list_model)
        self.api_list_view.setGeometry(10, 10, 540, 140)
        self.api_list_view.selectionModel().selectionChanged.connect(self.update_button_state)
        self.api_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.api_list_view.customContextMenuRequested.connect(self.show_context_menu)

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
        self.delete_button.setGeometry(450, 160, 100, 30)
        self.delete_button.clicked.connect(self.delete)

        self.edit_button = QPushButton("Edit", self)
        self.edit_button.setEnabled(False)
        self.edit_button.setGeometry(340, 160, 100, 30)
        self.edit_button.clicked.connect(self.edit)

    def show_context_menu(self, pos):
        """
        Called when the user right clicks in api_list_view.
        """
        index = self.api_list_view.indexAt(pos)
        if index.isValid(): # If the user right clicked on an item
            menu = QMenu(self)

            edit_option = menu.addAction('Edit')
            edit_option.triggered.connect(self.edit)

            delete_option = menu.addAction('Delete')
            delete_option.triggered.connect(self.delete)

            if index.row() > 0:
                move_up_option = menu.addAction('Move Up')
                move_up_option.triggered.connect(self.move_up)

            if index.row() < len(self.api_list_model.sources) - 1:
                move_down_option = menu.addAction('Move Down')
                move_down_option.triggered.connect(self.move_down)

            if self.api_list_model.sources[index.row()]["enabled"] == True:
                disable_option = menu.addAction('Disable')
                disable_option.triggered.connect(self.disable)

            else:
                enable_option = menu.addAction('Enable')
                enable_option.triggered.connect(self.enable)

            menu.exec_(self.mapToGlobal(pos))

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
        text, ok = QInputDialog.getText(self, "Input New URL", f"Please input the URL you would like to add:\t\t\t\t{chr(160)}") # Adds whitespace at the end of the line to widen window
        if ok:
            if text.startswith('http'):
                self.api_list_model.sources.append({"url": text, "enabled": True})
                self.api_list_model.update()
            else:
                QMessageBox.information(self, "Error", "Invalid URL! Must begin with 'http' or 'https'", QMessageBox.Ok)

    def delete(self):
        """
        Handles the delete button being clicked.
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            del self.api_list_model.sources[index.row()]
            self.api_list_model.update()
            self.api_list_view.clearSelection()

    def edit(self):
        """
        Handles the edit button being clicked.
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        if selected_indexes:            
            index = selected_indexes[0]
            text, ok = QInputDialog.getText(self, "Edit URL", f"Input edited URL:\t\t\t\t\t\t\t{chr(160)}", text=self.api_list_model.sources[index.row()]["url"]) # Adds whitespace at the end of the line to widen window
            if ok:
                if text.startswith('http'):
                    self.api_list_model.sources[index.row()]["url"] = text
                    self.api_list_model.update()
                else:
                    QMessageBox.information(self, "Error", "Invalid URL! Must begin with 'http' or 'https'", QMessageBox.Ok)

    def move_up(self):
        """
        Moves the selected row up 1 position in the table.
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0].row()
            self.api_list_model.sources.insert(index - 1, self.api_list_model.sources.pop(index))
            self.api_list_model.update()

    def move_down(self):
        """
        Moves the selected row down 1 position in the table.
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0].row()
            self.api_list_model.sources.insert(index + 1, self.api_list_model.sources.pop(index))
            self.api_list_model.update()

    def disable(self):
        """
        Disables the selected API.
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0].row()
            self.api_list_model.sources[index]["enabled"] = False
            self.api_list_model.update()

    def enable(self):
        """
        Enables the selected API.
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0].row()
            self.api_list_model.sources[index]["enabled"] = True
            self.api_list_model.update()

    def update_button_state(self):
        """
        Updates the state of the edit and delete buttons (called when selection changes).
        """
        selected_indexes = self.api_list_view.selectedIndexes()
        self.delete_button.setEnabled(bool(selected_indexes))
        self.edit_button.setEnabled(bool(selected_indexes))


class API_list_model(QAbstractListModel):
    """
    Class to model the list of URLs.
    """

    def __init__(self, api):
        """
        Initializes the model.
        """
        self.api = api
        super(API_list_model, self).__init__()
        try:
            with open("config.json", 'r') as config_file:
                config = json.load(config_file)

            if "urls" in config.keys(): # Detect and fix outdated config.json files
                self.config = {"sources": []}
                for url in config["urls"]:
                    self.config["sources"].append({"url": url, "enabled": True})
                with open("config.json", 'w') as config_file:
                    json.dump(self.config, config_file)

            else:
                self.config = config

        except FileNotFoundError:
            self.config = {"sources": []}
            with open("config.json", "w") as config_file:
                json.dump(self.config, config_file)
        self.sources = self.config["sources"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if self.sources[index.row()]["enabled"] == True:
                return self.sources[index.row()]["url"].split("?")[0] + "..."
            else:
                return f"(disabled) {self.sources[index.row()]['url'].split('?')[0]}..."

    def rowCount(self, index):
        return len(self.sources)

    def update(self):
        """
        Updates config file and applies the changes wherever needed.
        """
        self.layoutChanged.emit()
        self.config["sources"] = self.sources
        with open("config.json", "w") as config_file:
            json.dump(self.config, config_file)
        if self.api.api_process:
            self.api.kill_api()
            self.api.start_api()
