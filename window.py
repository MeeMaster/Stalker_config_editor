import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QSpacerItem, QAction, QTabWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QSizePolicy,
                             QFileDialog, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from collapsible import CollapsibleBox
from constants import *
from item_stats_display import ItemStatsDisplay
from functools import partial
from view_classes import *  # EditableGridView, QLabelClickable, SelectionWindow, SimpleView

simple_view = True


class MainWindow(QMainWindow):
    directory_signal = pyqtSignal(str, str)
    view_switch_signal = pyqtSignal(bool)
    save_data = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.title = 'S.T.A.L.K.E.R config editor'
        self.left = 20
        self.top = 30
        self.width = 1600
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Add menu bar
        bar = self.menuBar()
        file = bar.addMenu("File")
        view = bar.addMenu("View")
        simple_view_toggle = QAction("Simple", self)
        simple_view_toggle.setCheckable(True)
        simple_view_toggle.setChecked(simple_view)
        view.addAction(simple_view_toggle)
        view.triggered[QAction].connect(self.process_trigger)
        file.addAction("Open")
        file.addAction("Read gamedata")
        save = QAction("Save", self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        exit_action = QAction("Quit", self)
        file.addAction(exit_action)
        file.triggered[QAction].connect(self.process_trigger)

        # Add main widget
        self.window_widget = MyWindowWidget(self)
        self.setCentralWidget(self.window_widget)
        self.show()

    def open_file_name_dialog(self, read, title):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dirpath = file_dialog.getExistingDirectory(self, title,
                                                   os.getcwd(), options=options)
        if not dirpath:
            return

        self.directory_signal.emit(dirpath, read)

    def process_trigger(self, q):
        if q.text() == "Open":
            self.open_file_name_dialog("read", "Select directory with unpacked databases")
        if q.text() == "Simple":
            global simple_view
            simple_view = q.isChecked()
            self.window_widget.update_layout()
        if q.text() == "Save":
            self.open_file_name_dialog("write", "Select write destination")
        if q.text() == "Read gamedata":
            self.open_file_name_dialog("gamedata", "Select gamedata directory")


class MyWindowWidget(QWidget):
    item_signal = pyqtSignal(str)
    section_signal = pyqtSignal(str)
    value_changed = pyqtSignal(str, str)
    fill_request = pyqtSignal(object, list, str)
    tab_change = pyqtSignal(int)
    craft_update = pyqtSignal(dict)

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        # Initialize data holders
        self.names, self.descriptions = {}, {}
        self.reader = None
        self.name_dict = {}
        self.current_display_item = None

        # Create two (three?) panels
        self.main_layout = QHBoxLayout(self)
        self.list_layout = QVBoxLayout(self)
        self.values_layout = QVBoxLayout(self)
        self.images_layout = QVBoxLayout(self)

        # Add layouts
        self.main_layout.addLayout(self.list_layout, 1.5)
        self.main_layout.addLayout(self.values_layout, 3)
        self.main_layout.addLayout(self.images_layout, 1.5)

        # Initialize dropdown box
        self.sections = QComboBox()
        self.sections.addItems(["Ammo", "Armor", "Artifacts", "Consumables",
                                "Devices", "Equipment", "Tools", "Weapons", "Other"])
        self.sections.currentIndexChanged.connect(self.change_section)
        self.list_layout.addWidget(self.sections)
        self.item_scroll_widget = QScrollArea()
        self.item_scroll_widget.setWidgetResizable(True)
        self.list_layout.addWidget(self.item_scroll_widget)

        # Add tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.emit_tab_change)
        self.item_tab = QWidget()
        self.crafting_tab = QWidget()
        # self.trader_tab = QWidget()
        self.tabs.addTab(self.item_tab, "Item parameters")
        self.tabs.addTab(self.crafting_tab, "Crafting")
        # self.tabs.addTab(self.trader_tab, "Trade")
        self.values_layout.addWidget(self.tabs)

        # Item tab layout
        self.values_scroll_layout = QVBoxLayout()
        self.value_scroll_widget = QScrollArea()
        self.value_scroll_widget.setWidgetResizable(True)
        self.values_scroll_layout.addWidget(self.value_scroll_widget)
        self.item_tab.setLayout(self.values_scroll_layout)

        # Crafting tab layout
        self.craft_tab_layout = QVBoxLayout()
        self.craft_view = CraftingView()
        self.craft_view.fill_request.connect(self.send_fill_request)
        self.craft_view.value_change.connect(self.update_crafting)
        self.craft_tab_layout.addWidget(self.craft_view)
        self.crafting_tab.setLayout(self.craft_tab_layout)

        # Add icon display
        self.icon_widget = ItemStatsDisplay()
        self.images_layout.addWidget(self.icon_widget)

        self.update_layout()

    def update_crafting(self, crafting_info):
        self.craft_update.emit(crafting_info)

    def update_layout(self):
        self.setLayout(self.main_layout)
        self.display_value_data(self.current_display_item)

    def change_section(self):
        current_section = self.sections.currentText()
        self.section_signal.emit(current_section)

    def emit_tab_change(self, index):
        self.tab_change.emit(index)

    # def display_icon(self, icon):
    #     self.icon_widget.setPixmap(icon)

    def display_value_data(self, entry):
        if entry is None:
            return
        self.current_display_item = entry
        if simple_view:
            item_list_widget = self.build_simple_view(entry)
        else:
            item_list_widget = self.build_full_view(entry)
        self.value_scroll_widget.setWidget(item_list_widget)

    def build_full_view(self, entry):

        item_list_widget_layout = QVBoxLayout()
        item_list_widget = QWidget()
        main_widget = EditableGridView()
        main_widget.value_changed.connect(lambda x, y: self.value_changed.emit(x, y))
        item_list_widget_layout.addWidget(main_widget)
        base_entries = [line_entry for line_name, line_entry in entry.properties.items()
                        if line_entry.name == entry.name]
        main_widget.fill_from_list(base_entries)
        inheritances = set([line_entry.name for line_name, line_entry in entry.properties.items()
                            if line_entry.name != entry.name])
        for key in sorted(inheritances):
            entries = [line_entry for line_name, line_entry in entry.properties.items() if line_entry.name == key]
            box = CollapsibleBox("Inherited from {}".format(key))
            item_list_widget_layout.addWidget(box)
            lay = QVBoxLayout()
            dict_widget = EditableGridView()
            dict_widget.value_changed.connect(self.change_value)
            dict_widget.fill_from_list(entries)
            lay.addWidget(dict_widget)
            box.setContentLayout(lay)
        item_list_widget_layout.addStretch()
        item_list_widget.setLayout(item_list_widget_layout)
        return item_list_widget

    def build_simple_view(self, entry):
        item_list_widget_layout = QVBoxLayout()
        item_list_widget = QWidget()
        entries = [line_entry for line_name, line_entry in entry.properties.items() if
                   line_name in simple_categories]
        for line_entry in entries:
            if line_entry.prop in sliders:
                recalculation_functions = (calculate_normal_to_int, calculate_int_to_normal)
                if entry.is_artifact():
                    if line_entry.prop in artifact_params_coeffs:
                        recalculation_functions = (partial(calculate_points_to_val,
                                                           coeff=artifact_params_coeffs[line_entry.prop]),
                                                   partial(calculate_val_to_points,
                                                           coeff=artifact_params_coeffs[line_entry.prop]))

                if line_entry.prop in armor_params_coeffs:
                    recalculation_functions = (partial(calculate_points_to_val,
                                                       coeff=armor_params_coeffs[line_entry.prop]),
                                               partial(calculate_val_to_points,
                                                       coeff=armor_params_coeffs[line_entry.prop]))
                if line_entry.prop in food_params_coeffs:
                    recalculation_functions = (partial(calculate_points_to_val,
                                                       coeff=food_params_coeffs[line_entry.prop]),
                                               partial(calculate_val_to_points,
                                                       coeff=food_params_coeffs[line_entry.prop]))
                widget = SimpleView(True, recalculation_functions)
                if entry.is_artifact() and line_entry.prop in artifact_units:
                    unit = artifact_units[line_entry.prop]
                    min_val = minimal_values[unit]
                    max_val = maximal_values[unit]
                else:
                    min_val = minimal_values[line_entry.prop] if line_entry.prop in minimal_values else -1000.
                    max_val = maximal_values[line_entry.prop] if line_entry.prop in maximal_values else 1000.
                step = 1
                widget.set_min_max_step(min_val, max_val, step)
            elif line_entry.prop in selections:
                widget = SelectionWidget(line_entry)
                widget.fill_request.connect(self.send_fill_request)
            else:
                widget = SimpleView()
            widget.value_changed.connect(lambda x, y: self.value_changed.emit(x, y))
            item_list_widget_layout.addWidget(widget)
            # item_type = entry.get_item_type()
            widget.fill_from_input_line(line_entry, entry.get_item_type())
        item_list_widget_layout.addStretch()
        item_list_widget.setLayout(item_list_widget_layout)
        return item_list_widget

    def send_fill_request(self, function, name, is_type):
        self.fill_request.emit(function, name, is_type)

    def change_value(self, name, value):
        self.value_changed.emit(name, value)

    def display_item_list(self, item_dict):
        widget = self.get_list_widget_from_dict(item_dict)
        self.item_scroll_widget.setWidget(widget)
        self.update_layout()

    def get_list_widget_from_dict(self, data_dict):
        item_list_widget_layout = QVBoxLayout()
        item_list_widget = QWidget()
        for key in sorted(data_dict.keys()):
            if len(data_dict[key]) == 0:
                continue
            box = CollapsibleBox("{}".format(key))
            item_list_widget_layout.addWidget(box)
            lay = QVBoxLayout()
            for name, tag in sorted(data_dict[key]):
                label = QLabelClickable("{}".format(name))
                label.native_name = tag
                label.setAlignment(Qt.AlignCenter)
                label.clicked.connect(self.push_item_click)
                lay.addWidget(label)
            box.setContentLayout(lay)
        item_list_widget_layout.addStretch()
        item_list_widget.setLayout(item_list_widget_layout)
        return item_list_widget

    def push_item_click(self, name_tag):
        self.item_signal.emit(name_tag)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())