from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QSpacerItem, QSizePolicy, QSlider

from constants import simple_categories, artifact_simple_names, artifact_units, food_units, selections
from description_reader import translated_names
from images import load_icon_from_entry
from entry_classes import LineEntry

fill_request = pyqtSignal(object, list, str)


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
        self.single_item = False
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

    def set_single(self, setting):
        self.single_item = setting

    def cancel(self):
        self.close()

    def add_entry(self, name):
        if self.single_item:
            self.selected_entries = {name: self.available_entries[name]}
        else:
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
    value_changed = pyqtSignal(str, int)

    def __init__(self, label):
        SelectionGridView.__init__(self, label)
        self.single = False

    def fill_from_list(self, l):
        self.grid_layout = QGridLayout()
        l = [entry for entry in l if entry.name in translated_names]
        for index, entry in enumerate(l):
            column_index = index % self.maxwidth
            row_index = index // self.maxwidth
            widget = CraftingItemRepresentation(entry)
            widget.value_changed.connect(self.emit_change)
            widget.set_single_item(self.single)
            widget.load_data(entry)
            self.grid_layout.addWidget(widget, row_index, column_index)

        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(grid_widget)
        self.setLayout(self.main_layout)

    def emit_change(self, name, value):
        self.value_changed.emit(name, value)

    def set_single_item(self, setting):
        self.single = setting


class ItemRepresentation(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, entry):
        QWidget.__init__(self)
        self.entry = entry
        self.main_layout = QVBoxLayout()
        self.image = QLabel()
        self.image.setFixedWidth(100)
        self.image.setFixedHeight(100)
        self.image.setAlignment(Qt.AlignCenter)
        self.label = QLabel()
        self.label.setMaximumWidth(70)
        self.label.setAlignment(Qt.AlignCenter)
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
    value_changed = pyqtSignal(str, int)

    def __init__(self, entry):
        ItemRepresentation.__init__(self, entry)
        self.counter_layout = QHBoxLayout()
        self.main_layout.addLayout(self.counter_layout)
        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(15)
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(15)
        self.value_view = QLabel()
        self.value_view.setAlignment(Qt.AlignCenter)
        self.value_view.setFixedWidth(15)
        self.counter_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.counter_layout.addWidget(self.minus_button)
        self.counter_layout.addWidget(self.value_view)
        self.counter_layout.addWidget(self.plus_button)
        self.counter_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.minus_button.clicked.connect(lambda: self.change_value(False))
        self.plus_button.clicked.connect(lambda: self.change_value(True))
        self.single = False
        self.update_view()

    def change_value(self, add=True):
        if self.single:
            return
        if add:
            self.entry.add()
        else:
            self.entry.remove()
        self.update_view()
        self.value_changed.emit(self.entry.name, self.entry.quantity)

    def set_single_item(self, setting):
        self.single = setting
        self.minus_button.setEnabled(not setting)
        self.plus_button.setEnabled(not setting)

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
    value_change = pyqtSignal(dict)

    def __init__(self):
        QWidget.__init__(self)
        self.crafting_info = {}
        self.global_layout = QVBoxLayout()
        self.setLayout(self.global_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.global_layout.addWidget(self.scroll_area)

        self.main_widget = QWidget()
        self.scroll_area.setWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        # for n in range(20):
        #     self.global_layout.addWidget(QLabel("Dupa"))

    def fill_values(self, crafting_info):
        self.clear()
        self.crafting_info = crafting_info
        ### Make this iterative!
        counter = 1
        for recipe_name, recipe in self.crafting_info["craft"].items():
            booklet = recipe["craft_requirements"][1]
            if booklet is None:
                booklet = {}
            else:
                booklet = booklet.todict()

            # self.wid = QWidget()
            # layout = QVBoxLayout()
            # self.wid.setLayout(layout)
            label = QLabel("Recipe #{}".format(counter))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font: bold 20px;")
            craft_recipe_widget = ComponentDisplay(booklet, "Recipe")
            craft_recipe_widget.set_single_item(True)
            craft_recipe_widget.setMinimumHeight(350)
            craft_recipe_widget.set_part_type("booklets")
            craft_recipe_widget.set_recipe_name(recipe_name+"_recipe")
            craft_recipe_widget.value_change.connect(self.change_recipe)
            craft_recipe_widget.fill_request.connect(self.send_fill_request)

            crafting_widget = ComponentDisplay(crafting_info["craft"][recipe_name]["entries"], "Crafting")
            crafting_widget.set_single_item(False)
            crafting_widget.set_part_type("all")
            crafting_widget.setMinimumHeight(350)
            crafting_widget.value_change.connect(self.change_crafting_info)
            crafting_widget.fill_request.connect(self.send_fill_request)
            crafting_widget.set_recipe_name(recipe_name)

            self.main_layout.addWidget(label)
            self.main_layout.addWidget(craft_recipe_widget)
            self.main_layout.addWidget(crafting_widget)

            # self.main_layout.addWidget(self.wid)
            counter += 1

        disassembly_widget = ComponentDisplay(crafting_info["disassemble"], "Disassembling")
        disassembly_widget.set_single_item(False)
        disassembly_widget.setMinimumHeight(350)
        disassembly_widget.set_part_type("parts")
        # disassembly_widget.set_recipe_name("disassemble")
        disassembly_widget.value_change.connect(self.change_disassembling_info)
        disassembly_widget.fill_request.connect(self.send_fill_request)

        self.main_layout.addWidget(disassembly_widget)
        self.main_widget.setLayout(self.main_layout)
        self.update()

    def clear(self):
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)

    def change_recipe(self, name, value):
        name = name.replace("_recipe", "")
        craft_req = list(self.crafting_info["craft"][name]["craft_requirements"])

        craft_req[1] = list(value.values())[0] if list(value.values()) else None
        self.crafting_info["craft"][name]["craft_requirements"] = tuple(craft_req)
        self.send_change()

    def change_disassembling_info(self, name, value):
        self.crafting_info["disassemble"] = value
        self.send_change()

    def change_crafting_info(self, name, value):
        self.crafting_info["craft"][name]["entries"] = value
        self.send_change()  # Pass recipe name!

    def send_fill_request(self, function, name, request_type):
        self.fill_request.emit(function, name, request_type)

    def send_change(self):
        self.value_change.emit(self.crafting_info)


class ComponentDisplay(QWidget):
    fill_request = pyqtSignal(object, list, str)
    value_change = pyqtSignal(str, dict)

    def __init__(self, entries, name):
        QWidget.__init__(self)
        if entries is None:
            return
        self.popup = None
        self.selected_entries = entries
        self.recipe_name = ""

        self.main_layout = QVBoxLayout()
        self.chosen_items = CraftingSelectionGridView(name)
        self.chosen_items.value_changed.connect(self.update_quantity)
        self.main_layout.addWidget(self.chosen_items)
        self.button_layout = QHBoxLayout()

        self.mock_entry = LineEntry("", 0, "", "Components", list(self.selected_entries.keys()), "")

        self.change_widget = CraftingSelectionWidget(self.mock_entry, None)
        self.change_widget.value_changed.connect(self.change_value)
        self.change_widget.fill_request.connect(self.send_fill_request)
        self.main_layout.addWidget(self.change_widget)

        self.update_display()
        self.setLayout(self.main_layout)

    def set_single_item(self, setting):
        self.change_widget.set_single_item(setting)
        self.chosen_items.set_single_item(setting)

    def set_recipe_name(self, name):
        self.recipe_name = name

    def set_part_type(self, part_type):
        self.change_widget.set_selection_type(part_type)

    def send_fill_request(self, function, name, request_type):
        self.fill_request.emit(function, name, request_type)
        # fill_request.emit(function, name, request_type)

    def change_value(self, data):
        from entry_classes import CraftingEntry
        for item_name, item in data.items():
            if item_name in self.selected_entries:
                continue
            craft_entry = CraftingEntry()
            craft_entry.load_from_entry(item)
            craft_entry.quantity = 1
            self.selected_entries[item_name] = craft_entry
        for item_name in list(self.selected_entries.keys()):
            if item_name not in data:
                del(self.selected_entries[item_name])
        self.mock_entry = LineEntry("", 0, "", "Components", list(self.selected_entries.keys()), "")
        self.change_widget.set_line_entry(self.mock_entry)
        self.emit_change()
        self.update_display()

    def update_quantity(self, name, quantity):
        self.selected_entries[name].quantity = quantity
        self.emit_change()

    def emit_change(self):
        self.value_change.emit(self.recipe_name, self.selected_entries)

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
        self.single_item = False
        layout.addWidget(self.button)

    def set_single_item(self, setting):
        self.single_item = setting

    def set_selection_type(self, selection_type):
        self.selection_type = selection_type

    def open_popup(self):
        self.popup = SelectionWindow()
        self.popup.set_single(self.single_item)
        selection = self.selection_type if self.selection_type is not None else self.line_entry.prop
        if selection not in selections:
            return
        self.fill_request.emit(self.popup, selections[selection], "prop" if self.selection_type is None else "type")  # TODO: FIX THIS SHIT
        self.fill_request.emit(self.popup, self.line_entry.value, "name")
        self.popup.ok_button.clicked.connect(self.ok_clicked)
        self.popup.cancel_button.clicked.connect(self.close_popup)
        self.popup.update_lists()
        self.popup.show()

    def set_line_entry(self, line_entry):
        self.line_entry = line_entry

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


class CraftingSelectionWidget(SelectionWidget):
    value_changed = pyqtSignal(dict)

    def __init__(self, line_entry, selection_type=None):
        SelectionWidget.__init__(self, line_entry, selection_type)

    def ok_clicked(self):
        value = self.popup.ok()
        self.change_value(value)
        self.close_popup()

    def change_value(self, value):
        self.value_changed.emit(value)


class TrueFalseSwitch(QWidget):
    value_changed = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.yes_button = QPushButton("Yes")
        layout.addWidget(self.yes_button)
        self.yes_button.clicked.connect(self.yes_pushed)
        self.yes_button.setCheckable(True)
        self.no_button = QPushButton("No")
        layout.addWidget(self.no_button)
        self.no_button.clicked.connect(self.no_pushed)
        self.no_button.setCheckable(True)

    def yes_pushed(self):
        self.yes_button.setChecked(True)
        self.no_button.setChecked(False)
        self.value_changed.emit("true")

    def no_pushed(self):
        self.yes_button.setChecked(False)
        self.no_button.setChecked(True)
        self.value_changed.emit("false")

    def set_default(self, value):
        if value == "true":
            self.yes_button.setChecked(True)
            self.no_button.setChecked(False)
        elif value == "false":
            self.yes_button.setChecked(False)
            self.no_button.setChecked(True)


class SimpleView(QWidget):
    value_changed = pyqtSignal(str, str)

    def __init__(self, view_type="text", translation_functions=(None, None)):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.name_box = QLabel()
        self.view_type = view_type
        self.line_entry = None
        self.translation_functions = translation_functions

        self.unit_fill = "{:3.1f}%"
        self.divider = 10

        layout.addWidget(self.name_box)
        layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        if self.view_type == "slider":
            self.value = QSlider(Qt.Horizontal)
            self.value.valueChanged.connect(self.change_value)
        elif self.view_type == "text":
            self.value = QLineEdit()
            self.value.editingFinished.connect(self.change_value)
        elif self.view_type == "switch":
            self.value = TrueFalseSwitch()
            self.value.value_changed.connect(self.change_value)
        self.value.setFixedWidth(400)
        self.default = QLabel()
        self.default.setFixedWidth(70)
        layout.addWidget(self.value)
        if self.view_type == "slider":
            self.curr_val = QLabel()
            self.curr_val.setFixedWidth(70)
            layout.addWidget(self.curr_val)
        layout.addWidget(self.default)

    def set_min_max_step(self, minimum, maximum, step):
        if self.view_type == "slider":
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
        if self.view_type == "slider":
            value = float(line_entry.value[0])
            if self.translation_functions[0] is not None:
                value = self.translation_functions[0](value=float(line_entry.value[0]))
            self.curr_val.setText(self.unit_fill.format(value / self.divider))
            self.default.setText(self.unit_fill.format(value / self.divider))
            self.value.setValue(value)
        elif self.view_type == "text":
            self.value.setText(",".join(line_entry.value))
            self.default.setText(",".join(line_entry.value))
        elif self.view_type == "switch":
            self.value.set_default(line_entry.value[0])
            self.default.setText(",".join(line_entry.value))

    def change_value(self, value=None):
        if self.view_type == "slider":
            self.curr_val.setText(self.unit_fill.format(value / self.divider))
            if self.translation_functions[1] is not None:
                value = self.translation_functions[1](value=value)
        elif self.view_type == "text":
            value = self.value.text()
        value = str(value)
        self.value_changed.emit(self.line_entry.prop, value)