from PyQt5.QtWidgets import (QPushButton, QWidget, QSpacerItem, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                             QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from images import load_icon_from_entry

from description_reader import translated_names


class SelectionWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.line_entry = None
        self.item_characteristic = None
        self.selected_entries = {}
        self.available_entries = {}
        self.setFixedWidth(800)
        self.setWindowTitle("Choose items")
        # Set up layout
        self.setWindowModality(Qt.ApplicationModal)
        self.main_layout = QVBoxLayout()

        self.available_items_layout = QVBoxLayout()
        self.available_item_scroll_widget = QScrollArea()
        self.available_item_scroll_widget.setWidgetResizable(True)
        self.available_items_layout.addWidget(self.available_item_scroll_widget)
        self.available_items_widget = SelectionGridView("Available items")
        self.available_items_widget.entry_changed.connect(self.add_entry)
        self.available_item_scroll_widget.setWidget(self.available_items_widget)
        self.main_layout.addLayout(self.available_items_layout, 4)

        self.selected_items_layout = QVBoxLayout()
        self.selected_item_scroll_widget = QScrollArea()
        self.selected_item_scroll_widget.setWidgetResizable(True)
        self.selected_items_layout.addWidget(self.selected_item_scroll_widget)
        self.selected_items_widget = SelectionGridView("Selected items")
        self.selected_items_widget.entry_changed.connect(self.remove_entry)
        self.selected_item_scroll_widget.setWidget(self.selected_items_widget)
        self.main_layout.addLayout(self.selected_items_layout, 2)

        self.buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(self.buttons_layout, 1)
        self.ok_button = QPushButton("OK")
        # self.ok_button.clicked.connect(self.ok)
        self.cancel_button = QPushButton("Cancel")
        # self.cancel_button.clicked.connect(self.cancel)
        self.buttons_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.setLayout(self.main_layout)

    def ok(self):
        value = ",".join(item_name for item_name in self.selected_entries)
        return value

    def cancel(self):
        self.close()

    def add_entry(self, name):
        if name not in self.available_entries:
            return
        if name in self.selected_entries:
            return
        self.selected_entries[name] = self.available_entries[name]
        self.update_lists()

    def remove_entry(self, name):
        if name not in self.selected_entries:
            return
        del self.selected_entries[name]
        self.update_lists()

    def update_lists(self):
        self.available_items_widget.fill_from_list([item for name, item in self.available_entries.items()])
        self.selected_items_widget.fill_from_list([item for name, item in self.selected_entries.items()])

    def set_available_entries(self, entries):
        for entry in entries:
            self.available_entries[entry.name] = entry
        self.available_items_widget.fill_from_list(entries)

    def set_selected_entries(self, entries):
        for entry in entries:
            self.selected_entries[entry.name] = entry
        self.selected_items_widget.fill_from_list(entries)


class SelectionGridView(QWidget):
    entry_changed = pyqtSignal(str)

    def __init__(self, label):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.label = QLabel(label)
        self.label.setStyleSheet("font: bold 16px;")
        self.scroll_area = QScrollArea()
        self.grid_layout = QGridLayout()
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.scroll_area)
        self.maxwidth = 6

    def fill_from_list(self, l):
        self.grid_layout = QGridLayout()
        l = [entry for entry in l if entry.name in translated_names]
        for index, entry in enumerate(l):
            column_index = index % self.maxwidth
            row_index = index // self.maxwidth
            widget = ItemRepresentation(entry)
            widget.clicked.connect(self.emit_change)

            widget.load_data(entry)
            self.grid_layout.addWidget(widget, row_index, column_index)

        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(grid_widget)
        self.setLayout(self.main_layout)

    def emit_change(self, name):
        self.entry_changed.emit(name)


class ItemRepresentation(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, entry):
        QWidget.__init__(self)
        self.entry = entry
        self.main_layout = QVBoxLayout()
        self.image = QLabel()
        self.image.setFixedWidth(100)
        self.image.setFixedHeight(100)
        self.label = QLabel()
        self.label.setMaximumWidth(70)
        self.label.setWordWrap(True)
        self.main_layout.addWidget(self.image)
        self.main_layout.addWidget(self.label)
        self.load_data(entry)
        # self.connect(self.emit_change)
        self.setLayout(self.main_layout)

    def load_data(self, entry):
        self.label.setText(translated_names[entry.name])
        icon = load_icon_from_entry(entry)
        if icon is None:
            return
        self.image.setPixmap(icon)

    def mouseDoubleClickEvent(self, event):
        self.clicked.emit(self.entry.name)


