import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QSpacerItem, QAction, QTabWidget,
                             QVBoxLayout, QHBoxLayout, QSlider, QGridLayout, QLabel, QScrollArea, QSizePolicy,
                             QFileDialog, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from collapsible import CollapsibleBox
from constants import *
from selection_window import SelectionWindow
from item_stats_display import ItemStatsDisplay
from functools import partial

simple_view = True


class MainWindow(QMainWindow):
    directory_signal = pyqtSignal(str, bool)
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
        save = QAction("Save", self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        exit_action = QAction("Quit", self)
        file.addAction(exit_action)
        file.triggered[QAction].connect(self.process_trigger)

        # self.save_dir = None
        # Add main widget
        self.window_widget = MyWindowWidget(self)
        self.setCentralWidget(self.window_widget)
        self.show()

    def open_file_name_dialog(self, read):
        # if read or (not read and self.save_dir is None):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dirpath = file_dialog.getExistingDirectory(self, "QFileDialog.getExistingDirectory()",
                                                   os.getcwd(), options=options)
        #     if not read:
        #         self.save_dir = dirpath
        # else:
        #     dirpath = self.save_dir
        if not dirpath:
            return

        self.directory_signal.emit(dirpath, read)

    def process_trigger(self, q):
        if q.text() == "Open":
            self.open_file_name_dialog(True)
        if q.text() == "Simple":
            global simple_view
            simple_view = q.isChecked()
            self.window_widget.update_layout()
        if q.text() == "Save":
            self.open_file_name_dialog(False)


class MyWindowWidget(QWidget):
    item_signal = pyqtSignal(str)
    section_signal = pyqtSignal(str)
    value_changed = pyqtSignal(str, str)
    fill_request = pyqtSignal(object, str, bool)
    tab_change = pyqtSignal(int)

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
        # self.trader_tab = QWidget()
        # self.crafting_tab = QWidget()
        self.tabs.addTab(self.item_tab, "Item parameters")
        # self.tabs.addTab(self.trader_tab, "Trade")
        # self.tabs.addTab(self.crafting_tab, "Crafting")
        self.values_layout.addWidget(self.tabs)

        # Item tab layout
        self.values_scroll_layout = QVBoxLayout()
        self.value_scroll_widget = QScrollArea()
        self.value_scroll_widget.setWidgetResizable(True)
        self.values_scroll_layout.addWidget(self.value_scroll_widget)
        self.item_tab.setLayout(self.values_scroll_layout)
        self.update_layout()

        # Add icon display
        self.icon_widget = ItemStatsDisplay()
        self.images_layout.addWidget(self.icon_widget)

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


class QLabelClickable(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.native_name = None

    def mousePressEvent(self, ev):
        self.clicked.emit(self.native_name)

    # def unhighlight(self, *args):
    #     self.setStyleSheet("background-color: white")


class EditableGridView(QWidget):
    value_changed = pyqtSignal(str, str)

    def __init__(self, parent=None, maxwidth=3):
        QWidget.__init__(self, parent)
        self.maxwidth = maxwidth
        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def fill_from_list(self, l):
        for index, entry in enumerate(l):
            name = entry.prop
            # default_value = row["default_values"]
            default_value = "Default: {}".format(",".join(entry.default))
            current_value = entry.value
            column_index = index % self.maxwidth
            row_index = index // self.maxwidth
            widget = EditableBox(self)
            widget.value_changed.connect(self.change_value)
            widget.fill_values(name, default_value, current_value)
            self.layout.addWidget(widget, row_index, column_index)
        self.setLayout(self.layout)

    def change_value(self, name, value):
        self.value_changed.emit(name, value)


class EditableBox(QWidget):
    value_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # self.resize(150, 50)
        self.layout = QVBoxLayout()
        self.editable_widget = QLineEdit()
        self.editable_widget.setMaximumWidth(300)
        self.name_label = QLabel()
        self.default_value = QLabel()
        self.default_value.setMaximumWidth(300)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.editable_widget)
        self.layout.addWidget(self.default_value)
        self.editable_widget.editingFinished.connect(self.change_value)

    def fill_values(self, name, def_value, current_value):
        self.name_label.setText(name)
        self.default_value.setText(str(def_value))
        self.editable_widget.setText(",".join(current_value))
        self.setLayout(self.layout)

    def get_default_value(self):
        return self.default_value.text()

    def change_value(self):
        self.value_changed.emit(self.name_label.text(), self.editable_widget.text())


class ValueLineEdit(QLineEdit):
    edited = pyqtSignal(str, str, str)  # Strings of: entry_name, prop_name, value

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self.entry_name = None
        self.prop_name = None


class SelectionWidget(QWidget):
    value_changed = pyqtSignal(str, str)
    fill_request = pyqtSignal(object, str, bool)

    def __init__(self, line_entry):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.name_box = QLabel()
        self.line_entry = line_entry
        layout.addWidget(self.name_box)
        layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.button = QPushButton("Open editor")
        self.button.clicked.connect(self.open_popup)
        self.popup = None
        self.button.setFixedWidth(100)
        layout.addWidget(self.button)

    def open_popup(self):
        self.popup = SelectionWindow()
        self.fill_request.emit(self.popup, selections[self.line_entry.prop], True)
        self.fill_request.emit(self.popup, ",".join(self.line_entry.value), False)
        self.popup.ok_button.clicked.connect(self.ok_clicked)
        self.popup.cancel_button.clicked.connect(self.close_popup)
        self.popup.update_lists()
        self.popup.show()

    def ok_clicked(self):
        value = self.popup.ok()
        # self.line_entry.value = value
        self.change_value(value)
        self.close_popup()

    def close_popup(self):
        self.popup.close()
        self.popup = None

    def fill_from_input_line(self, line_entry):
        self.line_entry = line_entry
        self.name_box.setText(simple_categories[line_entry.prop])
        # self.value.setText(",".join(line_entry.value))
        # self.default.setText(",".join(line_entry.value))

    def change_value(self, value):
        value = str(value)
        self.value_changed.emit(self.line_entry.prop, value)


class SimpleView(QWidget):
    value_changed = pyqtSignal(str, str)

    def __init__(self, slider=False, translation_functions=(None, None)):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.name_box = QLabel()
        self.is_slider = slider
        self.line_entry = None
        self.translation_functions = translation_functions

        self.unit_fill = "{:3.1f}%"
        self.divider = 10

        layout.addWidget(self.name_box)
        layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        if slider:
            self.value = QSlider(Qt.Horizontal)
            self.value.valueChanged.connect(self.change_value)
        else:
            self.value = QLineEdit()
            self.value.editingFinished.connect(self.change_value)
        self.value.setFixedWidth(400)
        self.default = QLabel()
        self.default.setFixedWidth(70)
        layout.addWidget(self.value)
        if slider:
            self.curr_val = QLabel()
            self.curr_val.setFixedWidth(70)
            layout.addWidget(self.curr_val)
        layout.addWidget(self.default)

    def set_min_max_step(self, minimum, maximum, step):
        if self.is_slider:
            self.value.setMinimum(minimum)
            self.value.setMaximum(maximum)
            self.value.setSingleStep(step)

    def fill_from_input_line(self, line_entry, item_type):
        self.line_entry = line_entry

        self.name_box.setText(simple_categories[line_entry.prop])
        if item_type == "artifact":
            if line_entry.prop in artifact_simple_names:
                self.name_box.setText(artifact_simple_names[line_entry.prop])
            if line_entry.prop in artifact_units:
                self.unit_fill = "{} " + artifact_units[line_entry.prop]
                self.divider = 1
        if item_type == "food":
            if line_entry.prop in food_units:
                self.unit_fill = "{} " + food_units[line_entry.prop]
                self.divider = 1
        if self.is_slider:
            value = float(line_entry.value[0])
            if self.translation_functions[0] is not None:
                value = self.translation_functions[0](value=float(line_entry.value[0]))
            self.curr_val.setText(self.unit_fill.format(value / self.divider))
            self.default.setText(self.unit_fill.format(value / self.divider))
            self.value.setValue(value)
        else:
            self.value.setText(",".join(line_entry.value))
            self.default.setText(",".join(line_entry.value))

    def change_value(self, value=None):
        if self.is_slider:
            self.curr_val.setText(self.unit_fill.format(value / self.divider))
            if self.translation_functions[1] is not None:
                value = self.translation_functions[1](value=value)
        else:
            value = self.value.text()
        value = str(value)
        self.value_changed.emit(self.line_entry.prop, value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())