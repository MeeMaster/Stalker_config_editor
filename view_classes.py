from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QSpacerItem, QSizePolicy, QSlider

from constants import simple_categories, artifact_simple_names, artifact_units, food_units, selections
from description_reader import translated_names
from images import load_icon_from_entry
from file_reader import LineEntry


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


class QLabelClickable(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.native_name = None

    def mousePressEvent(self, ev):
        self.clicked.emit(self.native_name)


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
        # value = ",".join(item_name for item_name in self.selected_entries)
        return self.selected_entries  # value

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


class CraftingSelectionGridView(SelectionGridView):

    def __init__(self, label):
        SelectionGridView.__init__(self, label)

    def fill_from_list(self, l):
        self.grid_layout = QGridLayout()
        l = [entry for entry in l if entry.name in translated_names]
        for index, entry in enumerate(l):
            column_index = index % self.maxwidth
            row_index = index // self.maxwidth
            widget = CraftingItemRepresentation(entry)
            # widget.clicked.connect(self.emit_change)
            widget.load_data(entry)
            self.grid_layout.addWidget(widget, row_index, column_index)

        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(grid_widget)
        self.setLayout(self.main_layout)


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


class CraftingItemRepresentation(ItemRepresentation):
    def __init__(self, entry):
        ItemRepresentation.__init__(self, entry)
        self.counter_layout = QHBoxLayout()
        self.main_layout.addLayout(self.counter_layout)
        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(15)
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(15)
        self.value_view = QLabel()
        self.value_view.setFixedWidth(30)
        self.counter_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.counter_layout.addWidget(self.minus_button)
        self.counter_layout.addWidget(self.value_view)
        self.counter_layout.addWidget(self.plus_button)
        self.counter_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.minus_button.clicked.connect(lambda: self.change_value(False))
        self.plus_button.clicked.connect(lambda: self.change_value(True))
        self.update_view()

    def change_value(self, add=True):
        if add:
            self.entry.add()
        else:
            self.entry.remove()
        self.update_view()

    def update_view(self):
        self.value_view.setText(str(self.entry.quantity))

    # def load_data(self, entry):
    #     self.label.setText(translated_names[entry.name])
    #     # self.value_view.setText(str(entry.quantity))
    #     icon = load_icon_from_entry(entry)
    #     if icon is None:
    #         return
    #     self.image.setPixmap(icon)


class CraftingView(QWidget):
    fill_request = pyqtSignal(object, list, str)

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.crafting_widget = ComponentDisplay(None, "Crafting")
        self.disassembly_widget = ComponentDisplay(None, "Disassembling")
        self.main_layout.addWidget(self.crafting_widget)
        self.main_layout.addWidget(self.disassembly_widget)
        self.setLayout(self.main_layout)

    def fill_values(self, crafting_info):
        self.clear()
        # self.crafting_widget = ComponentDisplay(crafting_info["craft"], "Crafting")
        self.disassembly_widget = ComponentDisplay(crafting_info["disassemble"], "Disassembling")
        self.disassembly_widget.fill_request.connect(self.send_fill_request)

        # self.disassembly_widget.fill_display()
        # self.main_layout.addWidget(self.crafting_widget)
        self.main_layout.addWidget(self.disassembly_widget)
        self.setLayout(self.main_layout)
        self.update()
        # print("here")

    def clear(self):
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)

    def send_fill_request(self, function, name, request_type):
        self.fill_request.emit(function, name, request_type)



class ComponentDisplay(QWidget):
    fill_request = pyqtSignal(object, list, str)

    def __init__(self, entries, name):
        QWidget.__init__(self)
        if entries is None:
            return
        self.popup = None
        self.selected_entries = entries
        # self.available_entries = {}

        self.main_layout = QVBoxLayout()
        self.title = QLabel(name)
        self.main_layout.addWidget(self.title)
        self.chosen_items = CraftingSelectionGridView(name)
        self.main_layout.addWidget(self.chosen_items)
        self.button_layout = QHBoxLayout()

        mock_entry = LineEntry("", 0, "", "Components", "", list(self.selected_entries.keys()), "")
        self.change_widget = SelectionWidget(mock_entry, "parts")
        self.change_widget.fill_request.connect(self.send_fill_request)
        self.main_layout.addWidget(self.change_widget)
        # self.change_button.clicked.connect(self.open_popup)
        # self.button_layout.addWidget(self.change_button)

        # self.add_button = QPushButton("")
        # self.button_layout.addWidget(self.add_button)
        self.update_display()
        self.setLayout(self.main_layout)

    def send_fill_request(self, function, name, request_type):
        self.fill_request.emit(function, name, request_type)

    def update_display(self):
        # self.selected_entries = data["available"]
        item_list = [item for name, item in self.selected_entries.items()]
        self.chosen_items.fill_from_list(item_list)


class SelectionWidget(QWidget):
    value_changed = pyqtSignal(str, str)
    fill_request = pyqtSignal(object, list, str)

    def __init__(self, line_entry, selection_type=None):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.selection_type = selection_type
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
        selection = self.selection_type if self.selection_type is not None else self.line_entry.prop
        self.fill_request.emit(self.popup, selections[selection], "prop" if self.selection_type is None else "type")  # TODO: FIX THIS SHIT
        self.fill_request.emit(self.popup, self.line_entry.value, "name")
        self.popup.ok_button.clicked.connect(self.ok_clicked)
        self.popup.cancel_button.clicked.connect(self.close_popup)
        self.popup.update_lists()
        self.popup.show()

    def ok_clicked(self):
        value = self.popup.ok()
        value = ",".join(item_name for item_name in value)
        # self.line_entry.value = value
        self.change_value(value)
        self.close_popup()

    def close_popup(self):
        self.popup.close()
        self.popup = None

    def fill_from_input_line(self, line_entry, item_type):
        self.line_entry = line_entry
        self.name_box.setText(simple_categories[line_entry.prop])

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