from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QLineEdit, QHBoxLayout, QPushButton,\
    QSpacerItem, QSizePolicy, QSlider, QMenu, QAction, QComboBox, QTableWidget, QCheckBox
# from PyQt5.QtGui import QDoubleValidator, QIntValidator
from constants import simple_categories, artifact_simple_names, artifact_units, food_units, selections, \
    sections, basic_sections
from description_reader import translated_names
from entry_classes import LineEntry
from item_representations import ItemRepresentation, CraftingItemRepresentation, TradeItemRepresentation
import configs


class EditableGridView(QWidget):
    value_changed = pyqtSignal()

    def __init__(self, parent=None, maxwidth=3):
        QWidget.__init__(self, parent)
        self.maxwidth = maxwidth
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.entries = []

    def fill_from_list(self, l):
        self.entries = l
        for index, entry in enumerate(l):
            name = entry.prop
            current_value = entry.value
            column_index = index % self.maxwidth
            row_index = index // self.maxwidth
            widget = EditableBox()
            widget.value_changed.connect(self.change_value)
            widget.fill_values(entry)
            self.layout.addWidget(widget, row_index, column_index)
        self.setLayout(self.layout)

    def change_value(self):
        self.value_changed.emit()
        # self.value_changed.emit(name, value)


class SimpleView(QWidget):
    value_changed = pyqtSignal()

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
        self.value.setFixedWidth(350)
        self.default = QLabel()
        self.default.setMinimumWidth(100)
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

    def fill_from_input_line(self, line_entry, item_type=""):
        self.line_entry = line_entry
        name = simple_categories[line_entry.prop] if line_entry.prop in simple_categories else line_entry.prop
        self.name_box.setText(name)
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
        self.line_entry.value = [value]
        self.value_changed.emit()
        # self.value_changed.emit(self.line_entry.prop, value)


class QLabelClickable(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.native_name = None

    def mousePressEvent(self, ev):
        self.clicked.emit(self.native_name)


class EditableBox(QWidget):
    value_changed = pyqtSignal()
    # value_changed = pyqtSignal(str, str)

    def __init__(self):
        QWidget.__init__(self)
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
        self.entry = None

    def fill_values(self, entry):
        self.entry = entry
        self.name_label.setText(entry.prop)
        self.default_value.setText("Default: {}".format(",".join(entry.default)))
        self.editable_widget.setText(",".join(entry.value))
        self.setLayout(self.layout)

    def get_default_value(self):
        return self.default_value.text()

    def change_value(self):
        self.entry.value = [a.strip() for a in self.editable_widget.text().split()]
        self.value_changed.emit()


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
        self.available_items_widget.add_filter()
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
        self.available_items_widget.set_item_list([item for name, item in self.available_entries.items()])
        self.selected_items_widget.set_item_list([item for name, item in self.selected_entries.items()])

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

    def __init__(self, label=""):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.label_layout = QHBoxLayout()
        self.label = QLabel(label)
        self.label.setStyleSheet("font: bold 16px;")
        self.label_layout.addWidget(self.label)

        self.filter = FilterWidget()
        self.filter.filter_changed.connect(self.filter_items)

        self.scroll_area = QScrollArea()
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.label_layout)
        self.main_layout.addWidget(self.scroll_area)
        self.maxwidth = 6
        self.current_list = []
        self.item_repr = ItemRepresentation

    def set_name(self, name):
        self.label.setText(name)

    def set_item_list(self, l):
        self.current_list = l
        self.filter_items(*self.filter.get_current())

    def set_item_representation_type(self, item_type):
        self.item_repr = item_type

    def add_filter(self):
        self.label_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.label_layout.addWidget(self.filter)

    def fill_from_list(self, item_list):
        self.grid_layout = QGridLayout()
        item_list = [entry for entry in item_list if entry.name in translated_names]
        for index, entry in enumerate(item_list):
            widget = self.add_item_to_grid(index, entry)
            self.register_signals(widget)
        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(grid_widget)
        self.setLayout(self.main_layout)

    def register_signals(self, widget):
        widget.clicked.connect(self.emit_change)

    def add_item_to_grid(self, index, entry):
        column_index = index % self.maxwidth
        row_index = index // self.maxwidth
        widget = self.item_repr(entry)
        widget.load_data(entry)
        self.grid_layout.addWidget(widget, row_index, column_index)
        return widget

    def emit_change(self, name):
        self.entry_changed.emit(name)

    def filter_items(self, curr_text, curr_type):
        available_items = [entry for entry in self.current_list if entry.name in translated_names]
        if curr_type != "All":
            available_items = [entry for entry in available_items if entry.is_category(curr_type)]
        if curr_text:
            available_items = [entry for entry in available_items if curr_text.lower() in translated_names[entry.name].lower()]
        self.fill_from_list(available_items)


class ItemTypeSelection(QComboBox):
    value_changed = pyqtSignal(str)

    def __init__(self, has_all=True):
        QComboBox.__init__(self)
        self.items = []
        if has_all:
            self.items.append("All")
        if configs.basic_view:
            for key, values in basic_sections.items():
                for value in values:
                    self.items.append(value)
        else:
            for key, values in sections.items():
                for value in values:
                    self.items.append(value)
        self.addItems(self.items)


class CraftingSelectionGridView(SelectionGridView):
    value_changed = pyqtSignal(str, int)

    def __init__(self, label):
        SelectionGridView.__init__(self, label)
        self.single = False
        self.set_item_representation_type(CraftingItemRepresentation)

    def emit_change(self, name, value):
        self.value_changed.emit(name, value)

    def set_single_item(self, setting):
        self.single = setting

    def register_signals(self, widget):
        widget.clicked.connect(self.emit_change)
        widget.value_changed.connect(self.emit_change)


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
        self.add_recipe_button = QPushButton("Add recipe")
        self.add_recipe_button.setEnabled(False)
        self.add_recipe_button.clicked.connect(self.add_recipe)
        self.global_layout.addWidget(self.add_recipe_button)

        self.main_widget = QWidget()
        self.scroll_area.setWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

    def add_recipe(self):
        for letter in "abcdefghijklmnopqrstuvwxyz":
            new_name = letter + "_" + self.crafting_info["item"]
            if new_name in self.crafting_info["craft"]:
                continue
            self.crafting_info["craft"][new_name] = {"craft_requirements": (None, None), "entries": {}}
            self.fill_values(self.crafting_info)
            self.send_change()
            return

    def remove_recipe(self, name):
        if name in self.crafting_info["craft"]:
            del self.crafting_info["craft"][name]
        self.fill_values(self.crafting_info)
        self.send_change()

    def fill_values(self, crafting_info):
        self.clear()
        self.crafting_info = crafting_info
        self.add_recipe_button.setEnabled(True)
        ### Make this iterative!
        counter = 1
        for recipe_name, recipe in self.crafting_info["craft"].items():
            booklet = recipe["craft_requirements"][1]
            if booklet is None:
                booklet = {}
            else:
                booklet = booklet.todict()

            toolkit = recipe["craft_requirements"][0]
            if toolkit is None:
                toolkit = {}
            else:
                toolkit = toolkit.todict()

            wid = CraftingViewWidget()
            wid.set_item(recipe_name)
            wid.delete.connect(self.remove_recipe)
            label = QLabel("Recipe #{}".format(counter))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font: bold 20px;")
            wid.layout().addWidget(label)

            local_layout = QHBoxLayout()
            craft_recipe_widget = ComponentDisplay("Recipe")
            craft_recipe_widget.set_selection_grid_type(CraftingSelectionGridView)
            craft_recipe_widget.set_entries(booklet)
            craft_recipe_widget.set_single_item(True)
            craft_recipe_widget.setMinimumHeight(350)
            craft_recipe_widget.set_part_type("booklets")
            local_layout.addWidget(craft_recipe_widget)
            craft_recipe_widget.set_recipe_name(recipe_name+"_recipe")
            craft_recipe_widget.value_change.connect(self.change_recipe)
            craft_recipe_widget.fill_request.connect(self.send_fill_request)

            toolkit_widget = ComponentDisplay("Toolkit")
            toolkit_widget.set_selection_grid_type(CraftingSelectionGridView)
            toolkit_widget.set_entries(toolkit)
            toolkit_widget.set_single_item(True)
            toolkit_widget.setMinimumHeight(350)
            toolkit_widget.set_part_type("tools")
            toolkit_widget.set_recipe_name(recipe_name + "_toolkit")
            toolkit_widget.value_change.connect(self.change_toolkit)
            toolkit_widget.fill_request.connect(self.send_fill_request)
            local_layout.addWidget(toolkit_widget)
            wid.layout().addLayout(local_layout)

            crafting_widget = ComponentDisplay("Crafting")
            crafting_widget.set_selection_grid_type(CraftingSelectionGridView)
            crafting_widget.set_entries(crafting_info["craft"][recipe_name]["entries"])
            crafting_widget.set_single_item(False)
            crafting_widget.set_part_type("all")
            crafting_widget.setMinimumHeight(350)
            crafting_widget.value_change.connect(self.change_crafting_info)
            crafting_widget.fill_request.connect(self.send_fill_request)
            crafting_widget.set_recipe_name(recipe_name)
            wid.layout().addWidget(crafting_widget)

            self.main_layout.addWidget(wid)
            counter += 1

        disassembly_widget = ComponentDisplay("Disassembling")
        disassembly_widget.set_selection_grid_type(CraftingSelectionGridView)
        disassembly_widget.set_entries(crafting_info["disassemble"])
        disassembly_widget.set_single_item(False)
        disassembly_widget.setMinimumHeight(350)
        disassembly_widget.set_part_type("all")
        disassembly_widget.value_change.connect(self.change_disassembling_info)
        disassembly_widget.fill_request.connect(self.send_fill_request)
        self.main_layout.addWidget(disassembly_widget)
        cond_label = QLabel("Is using item condition*")
        cond_label.setToolTip("Switches the usage of component condition when disassembling. When this is enabled, only"
                              " one item of each type can be recovered (If you set that it uses e.g. 2 cloth sheets, "
                              "you will only get 1 during disassembly). If it is disabled, you CAN NOT repair the item "
                              "at the workbench.")
        cond_button = TrueFalseSwitch()
        cond_button.set_default(self.crafting_info["conditional"])
        cond_button.value_changed.connect(self.switch_conditionality)
        self.main_layout.addWidget(cond_label)
        self.main_layout.addWidget(cond_button)

        self.main_widget.setLayout(self.main_layout)
        self.update()

    def clear(self):
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            if item.widget() is None:
                layout = item.layout()
                for j in reversed(range(layout.count())):
                    widget = layout.itemAt(j).widget()
                    widget.setParent(None)
                continue
            item.widget().setParent(None)

    def switch_conditionality(self, value):
        self.crafting_info["conditional"] = value
        self.send_change()

    def change_recipe(self, name, value):
        name = name.replace("_recipe", "")
        craft_req = list(self.crafting_info["craft"][name]["craft_requirements"])

        craft_req[1] = list(value.values())[0] if list(value.values()) else None
        self.crafting_info["craft"][name]["craft_requirements"] = tuple(craft_req)
        self.send_change()

    def change_toolkit(self, name, value):
        name = name.replace("_toolkit", "")
        craft_req = list(self.crafting_info["craft"][name]["craft_requirements"])

        craft_req[0] = list(value.values())[0] if list(value.values()) else None
        self.crafting_info["craft"][name]["craft_requirements"] = tuple(craft_req)
        self.send_change()

    def change_disassembling_info(self, name, value):
        self.crafting_info["disassemble"] = value
        self.send_change()

    def change_crafting_info(self, name, value):
        # if change_type == "quantity":
        self.crafting_info["craft"][name]["entries"] = value
        self.send_change()  # Pass recipe name!

    def send_fill_request(self, function, name, request_type):
        self.fill_request.emit(function, name, request_type)

    def send_change(self):
        self.value_change.emit(self.crafting_info)


class CraftingViewWidget(QWidget):
    delete = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.menu = QMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu.addAction(QAction("Remove entire recipe", self))
        self.customContextMenuRequested.connect(self.show_header_menu)
        self.item = None

    def set_item(self, name):
        self.item = name

    def show_header_menu(self, point):
        self.menu.triggered[QAction].connect(self.resolve_action)
        self.menu.exec_(self.mapToGlobal(point))

    def add_header_option(self, option, target):
        self.menu.addAction(QAction(option, self))
        self.menu_actions[option] = target

    def resolve_action(self, action):
        if action.text() == "Remove entire recipe":
            self.remove()

    def remove(self):
        self.delete.emit(self.item)


class ComponentDisplay(QWidget):
    fill_request = pyqtSignal(object, list, str)
    value_change = pyqtSignal(str, dict)

    def __init__(self, name=""):
        QWidget.__init__(self)
        # if entries is None:
        #     return
        self.popup = None
        self.selected_entries = {}#entries
        self.recipe_name = ""

        self.main_layout = QVBoxLayout()
        self.chosen_items = SelectionGridView(name)
        self.main_layout.addWidget(self.chosen_items)
        self.button_layout = QHBoxLayout()
        self.mock_entry = None
        self.change_widget = CraftingSelectionWidget(None)
        self.change_widget.value_changed.connect(self.change_value)
        self.change_widget.fill_request.connect(self.send_fill_request)
        self.main_layout.addWidget(self.change_widget)

        self.update_display()
        self.setLayout(self.main_layout)

    def set_selection_grid_type(self, sel_grd_type):
        self.chosen_items.setParent(None)
        self.chosen_items = sel_grd_type(self.chosen_items.label.text())
        self.main_layout.insertWidget(0, self.chosen_items)
        self.chosen_items.value_changed.connect(self.update_quantity)

    def set_name(self, name):
        self.chosen_items.set_name(name)

    def set_entries(self, entries):
        self.selected_entries = entries
        self.mock_entry = LineEntry("", 0, "", "Components", list(self.selected_entries.keys()), "")
        self.change_widget.set_line_entry(self.mock_entry)
        self.update_display()

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
        item_list = [item for name, item in self.selected_entries.items()]
        self.chosen_items.set_item_list(item_list)


class SelectionWidget(QWidget):
    value_changed = pyqtSignal(str, str)
    fill_request = pyqtSignal(object, list, str)

    def __init__(self, selection_type=None):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.selection_type = selection_type
        self.name_box = QLabel()
        self.line_entry = None
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
        self.fill_request.emit(self.popup, selections[selection], "prop" if self.selection_type is None else "type")
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

    def __init__(self, selection_type=None):
        SelectionWidget.__init__(self, selection_type)

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


class TradeView(QWidget):
    fill_request = pyqtSignal(object, list, str)
    data_changed = pyqtSignal(dict)

    def __init__(self):
        QWidget.__init__(self)

        self.trade_dict = None

        self.scroll_layout = QVBoxLayout()
        self.setLayout(self.scroll_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_layout.addWidget(self.scroll_area)
        self.main_widget = QWidget()
        self.scroll_area.setWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.buy_condition = SimpleView("text")
        self.sell_condition = SimpleView("text")
        self.buy_price = SimpleView("text")
        self.sell_price = SimpleView("text")
        self.supply_widget = QWidget()
        self.supply_layout = QVBoxLayout()
        self.supply_widget.setLayout(self.supply_layout)
        self.main_layout.addWidget(self.buy_condition)
        self.main_layout.addWidget(self.sell_condition)
        self.discounts = DiscountViewWidget()
        self.supplies = SupplyViewWidget()
        self.main_layout.addWidget(self.buy_price)
        self.main_layout.addWidget(self.sell_price)
        self.main_layout.addWidget(self.discounts)
        self.main_layout.addWidget(self.supplies)
        self.main_layout.addWidget(self.supply_widget)
        self.main_widget.setLayout(self.main_layout)
        self.list_view = None

    def clear(self):
        for i in reversed(range(self.supply_layout.count())):
            item = self.supply_layout.itemAt(i)
            if item.widget() is None:
                continue
            item.widget().setParent(None)

    def set_data(self, trade_dict):
        self.trade_dict = trade_dict
        self.clear()
        self.buy_condition.fill_from_input_line(LineEntry("", 0, "", "Buy preset inherited from",
                                                          trade_dict["Buy_conditions"].parents, ""), "")
        self.buy_condition.value_changed.connect(self.change_buy_parent)
        self.sell_condition.fill_from_input_line(LineEntry("", 0, "", "Sell preset inherited from",
                                                           trade_dict["Sell_conditions"].parents, ""), "")
        self.sell_condition.value_changed.connect(self.change_sell_parent)
        if trade_dict["buy_item_exponent"] is None:
            self.buy_price.setEnabled(False)
        else:
            self.buy_price.setEnabled(True)
            self.buy_price.fill_from_input_line(trade_dict["buy_item_exponent"], "")
            self.buy_price.value_changed.connect(self.change_entry)
        if trade_dict["sell_item_exponent"] is None:
            self.sell_price.setEnabled(False)
        else:
            self.sell_price.setEnabled(True)
            self.sell_price.fill_from_input_line(trade_dict["sell_item_exponent"], "")
            self.sell_price.value_changed.connect(self.change_entry)

        # self.discounts.clear()
        self.discounts.set_data(self.trade_dict["discounts"])
        self.discounts.data_changed.connect(self.change_entry)
        self.supplies.set_data(self.trade_dict["Stock_info"])
        self.supplies.data_changed.connect(self.change_entry)
        self.list_view = TradingListView()
        self.list_view.data_changed.connect(self.change_entry)
        self.list_view.set_entry(self.trade_dict)
        self.supply_layout.addWidget(self.list_view)
        self.supply_widget.setLayout(self.supply_layout)

    def change_buy_parent(self):
        self.trade_dict["Buy_conditions"].parents = [self.buy_condition.value.text()]
        self.change_entry()

    def change_sell_parent(self):
        self.trade_dict["Sell_conditions"].parents = [self.sell_condition.value.text()]
        self.change_entry()

    def send_fill_request(self, function, name, request_type):
        self.fill_request.emit(function, name, request_type)

    def change_entry(self):
        self.trade_dict  # This forces the trade dict to update, I have no idea why it doesn't do that automatically
        self.data_changed.emit(self.trade_dict)


class DiscountViewWidget(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add discount")
        self.button_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.button_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_discount)
        self.main_layout.addLayout(self.button_layout)

        self.current_index = 0
        self.trade_data = None

    def add_widget(self, index):
        if self.trade_data is None:
            return
        new_widget = DiscountView()
        new_widget.set_data(self.trade_data, index)
        new_widget.data_changed.connect(self.emit_change)
        self.main_layout.insertWidget(index, new_widget)

    def set_data(self, data):
        self.clear()
        self.trade_data = data
        for discount_index, discount_value in enumerate(self.trade_data["line"].value):
            self.add_widget(discount_index)
            self.current_index = discount_index

    def add_discount(self):
        # nums = [0]
        # for name in self.trade_data:
        #     if "supplies_" not in name:
        #         continue
        #     num = name.replace("supplies_", "")
        #     try:
        #         int(num)
        #     except:
        #         continue
        #     nums.append(int(num))
        self.trade_data["line"].conditions.append("")
        self.trade_data["line"].value.append("")
        # self.trade_data["entries"]
        self.add_widget(self.current_index + 1)
        self.current_index += 1
        self.trade_data["line"].changed = True
        self.emit_change()

    def clear(self):
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            if item.widget() is None:
                continue
            item.widget().setParent(None)

    def emit_change(self):
        self.data_changed.emit()


class SupplyViewWidget(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add supply")
        self.button_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.button_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_supply)
        self.main_layout.addLayout(self.button_layout)

        self.current_index = 0
        self.trade_data = None

    def add_widget(self, index, supply_name):
        if self.trade_data is None:
            return
        new_widget = SupplyView()
        new_widget.set_data(self.trade_data, supply_name)
        new_widget.data_changed.connect(self.emit_change)
        self.main_layout.insertWidget(index, new_widget)

    def set_data(self, data):
        self.clear()
        self.trade_data = data
        for supply_index, supply_name in enumerate(sorted(self.trade_data.keys())):
            self.add_widget(supply_index, supply_name)
            self.current_index = supply_index

    def add_supply(self):
        nums = [0]
        for name in self.trade_data:
            if "supplies_" not in name:
                continue
            num = name.replace("supplies_", "")
            try:
                int(num)
            except:
                continue
            nums.append(int(num))
        last_num = max(nums)
        new_name = "supplies_{}".format(last_num+1)
        self.trade_data[new_name] = {"condition": "", "parent": ""}
        self.add_widget(self.current_index + 1, new_name)
        self.current_index += 1
        self.emit_change()

    def clear(self):
        self.current_index = 0
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            if item.widget() is None:
                continue
            item.widget().setParent(None)

    def emit_change(self):
        self.data_changed.emit()


class TradingSelectionGridView(CraftingSelectionGridView):
    value_changed = pyqtSignal(str, int)
    chance_changed = pyqtSignal(str, float)

    def __init__(self, label):
        SelectionGridView.__init__(self, label)
        self.set_item_representation_type(TradeItemRepresentation)

    def register_signals(self, widget):
        widget.clicked.connect(self.emit_change)
        widget.value_changed.connect(self.emit_change)
        widget.chance_changed.connect(self.emit_chance_change)

    def emit_chance_change(self, name, value):
        self.chance_changed.emit(name, value)


class TradingListView(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.label_layout = QHBoxLayout()
        self.entry_name = QLabel("Supplies and prices")
        self.entry_name.setStyleSheet("font: bold 16px;")
        self.entry_name.setAlignment(Qt.AlignCenter)
        self.filter = FilterWidget(False)
        self.filter.filter_changed.connect(self.filter_data)
        self.label_layout.addWidget(self.entry_name)
        self.label_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.label_layout.addWidget(self.filter)
        self.main_layout.addLayout(self.label_layout)
        self.table = QTableWidget()

        self.main_layout.addWidget(self.table)
        self.setLayout(self.main_layout)

        self.name = None
        self.trade_entry = None
        self.entry_order = {}

    def set_entry(self, trade_entry):
        self.trade_entry = trade_entry
        self.fill_table(self.filter.get_current())

    def fill_table(self, filters):
        self.table.setColumnCount(3 + len(self.trade_entry["Stocks"]))
        self.table.setMinimumHeight(500)
        curr_text, curr_sect = filters
        self.table.setHorizontalHeaderLabels(["Item", "Buy price factor", "Sell price factor"] +
                                             list(sorted(self.trade_entry["Stocks"].keys())))
        good_items = [item for item_name, item in self.trade_entry["Merch"].items() if item.category == curr_sect]
        if curr_text:
            good_items = [item for item in good_items if curr_text.lower() in translated_names[item.name].lower()]
        self.table.setRowCount(len(good_items))
        for index, item in enumerate(good_items):
            self.entry_order[item.name] = index
            self.set_item_at_index(index, item)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def set_item_at_index(self, index, item):
        representation = ItemRepresentation(item)
        self.table.setCellWidget(index, 0, representation)
        buy_price = TablePriceWidget()
        buy_price.set_data(item, self.trade_entry["Buy_conditions"])
        buy_price.data_changed.connect(self.change_price)
        self.table.setCellWidget(index, 1, buy_price)
        sell_price = TablePriceWidget()
        sell_price.set_data(item, self.trade_entry["Sell_conditions"])
        self.table.setCellWidget(index, 2, sell_price)
        sell_price.data_changed.connect(self.change_price)
        for index2, supply_name in enumerate(sorted(self.trade_entry["Stocks"].keys())):
            supply_widget = TableSupplyWidget()
            supply_widget.data_changed.connect(self.change_data)
            supply_widget.set_data(item.name, supply_name, self.trade_entry["Stocks"])
            self.table.setCellWidget(index, 3 + index2, supply_widget)

    def change_data(self, entry):
        # all_children = self.get_all_children(supply)
        item = self.trade_entry["Merch"][entry]
        self.set_item_at_index(self.entry_order[entry], item)
        self.data_changed.emit()

    def change_price(self):
        self.data_changed.emit()

    def get_all_children(self, supply_name):
        current_children = [supply_name]
        found = True
        while found:
            found = False
            for supply in self.trade_entry["Stocks"]:
                for parent in self.trade_entry["Stocks"][supply]["parent"]:
                    if parent not in current_children:
                        continue
                    if supply in current_children:
                        continue
                    current_children.append(supply)
                    found = True
        current_children.remove(supply_name)
        return current_children

    def filter_data(self, curr_text, curr_selection):
        self.fill_table((curr_text, curr_selection))

    def clear_table(self):
        self.entry_order = {}
        self.table.setRowCount(0)


class TablePriceWidget(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.supply_label = QLabel("Price")
        self.supply_edit = QLineEdit()
        self.supply_edit.setMaximumWidth(30)
        self.supply_edit.editingFinished.connect(self.change_data)
        self.main_layout.addWidget(self.supply_label)
        self.main_layout.addWidget(self.supply_edit)
        self.setLayout(self.main_layout)
        self.item = None
        self.price_entry = None

    def set_data(self, item, price_entry):
        self.item = item
        self.price_entry = price_entry
        if self.item.name not in price_entry.properties:
            value = 1
        else:
            value = price_entry.properties[self.item.name].value[0]
        if not value:
            value = 0
        self.supply_edit.setText(str(value))

    def change_data(self):
        new_value = self.supply_edit.text()
        new_value = ".".join(new_value.split(","))
        old_value = self.price_entry.properties[self.item.name].value[0] if \
            self.item.name in self.price_entry.properties else 1
        if not old_value:
            old_value = "0"
        if new_value == old_value:
            return
        if self.item.name not in self.price_entry.properties:
            mock_line = LineEntry(self.price_entry.file, -1, self.price_entry.name, self.item.name, [], "")
            self.price_entry.properties[self.item.name] = mock_line
        if new_value == "0":
            self.price_entry.properties[self.item.name].value = [""]
            self.price_entry.properties[self.item.name].equal_sign = False
            self.price_entry.properties[self.item.name].comment = "NO TRADE"
        else:
            self.price_entry.properties[self.item.name].value = [new_value, new_value]
        self.price_entry.changed = True
        self.data_changed.emit()


class TableSupplyWidget(QWidget):
    data_changed = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.supply_label = QLabel("Supply")
        self.supply_edit = QLineEdit()
        self.supply_edit.setMaximumWidth(30)
        self.supply_edit.editingFinished.connect(self.change_data)
        self.chance_label = QLabel("Chance")
        self.chance_edit = QLineEdit()
        self.chance_edit.setMaximumWidth(30)
        self.chance_edit.editingFinished.connect(self.change_data)
        self.main_layout.addWidget(self.supply_label)
        self.main_layout.addWidget(self.supply_edit)
        self.main_layout.addWidget(self.chance_label)
        self.main_layout.addWidget(self.chance_edit)
        self.setLayout(self.main_layout)

        self.entry_name = None
        self.supply_name = None
        self.supplies = None
        self.current_quantity = None
        self.current_chance = None

    def get_all_parents(self, supply_name):
        all_parents = []

        def get_parents(supply):
            for parent_name in self.supplies[supply].parents:
                if parent_name not in self.supplies:
                    continue
                all_parents.append(parent_name)
                get_parents(parent_name)
        get_parents(supply_name)
        return all_parents

    def set_data(self, entry_name, supply_name, supply_data):
        self.supplies = supply_data
        self.entry_name = entry_name
        self.supply_name = supply_name
        supply, chance = 0, 0
        if entry_name not in self.supplies[supply_name].properties:
            all_parents = self.get_all_parents(self.supply_name)
            for parent_name in all_parents:
                if entry_name in self.supplies[parent_name].properties:
                    supply, chance = self.supplies[parent_name].properties[entry_name].value
                    break
        else:
            supply, chance = self.supplies[supply_name].properties[entry_name].value
        self.current_quantity = int(supply)
        self.supply_edit.setText(str(supply))
        self.chance_edit.setText(str(chance))
        self.current_chance = float(chance)

    def change_data(self):
        changed = ""
        new_chance = self.chance_edit.text()
        new_chance = float(".".join(new_chance.split(",")))
        new_supply = int(self.supply_edit.text())

        latest_parent = self.supply_name
        if self.entry_name not in self.supplies[self.supply_name].properties:
            all_parents = self.get_all_parents(self.supply_name)
            for parent_name in all_parents:
                if self.entry_name in self.supplies[parent_name].properties:
                    latest_parent = parent_name
                    break

        if new_chance != self.current_chance or new_supply != self.current_quantity:
            if latest_parent != self.supply_name:
                new_line = LineEntry(self.supplies[self.supply_name].file, -1, self.supply_name, self.entry_name,
                                     [str(new_supply), str(new_chance)], conditions=["", ""])
                self.supplies[self.supply_name].properties[self.entry_name] = new_line
            else:
                if self.entry_name not in self.supplies[self.supply_name].properties:
                    new_line = LineEntry(self.supplies[self.supply_name].file, -1, self.supply_name, self.entry_name,
                                         [str(new_supply), str(new_chance)], conditions=["", ""])
                    self.supplies[self.supply_name].properties[self.entry_name] = new_line
                else:
                    self.supplies[self.supply_name].properties[self.entry_name].value = [str(new_supply), str(new_chance)]

        self.data_changed.emit(self.entry_name)


class FilterWidget(QWidget):
    filter_changed = pyqtSignal(str, str)

    def __init__(self, has_all=True):
        QWidget.__init__(self)
        self.main_layout = QHBoxLayout()
        self.name_filter = QLineEdit()
        self.name_filter.textChanged.connect(self.filter)
        self.name_filter.setMaximumWidth(150)
        self.type_filter = ItemTypeSelection(has_all)
        self.type_filter.currentIndexChanged.connect(self.filter)
        self.main_layout.addWidget(self.name_filter)
        self.main_layout.addWidget(self.type_filter)
        self.setLayout(self.main_layout)

    def get_current(self):
        return self.name_filter.text(), self.type_filter.currentText()

    def filter(self):
        self.filter_changed.emit(self.name_filter.text(), self.type_filter.currentText())


class SupplyView(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font: bold 16px;")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.conditions = SimpleView()
        self.conditions.value_changed.connect(self.change_condition_data)
        self.parents = SimpleView()
        self.parents.value_changed.connect(self.change_parent_data)
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.conditions)
        self.main_layout.addWidget(self.parents)
        self.setLayout(self.main_layout)

        self.supply_dict = None
        self.name = None

    def set_data(self, supply_dict, supply_name):
        self.supply_dict = supply_dict
        self.name = supply_name
        self.name_label.setText(supply_name)
        mock_line = LineEntry("", 0, "", "Conditions", [supply_dict[supply_name]["condition"]], "")
        self.conditions.fill_from_input_line(mock_line)
        mock_line = LineEntry("", 0, "", "Parents", supply_dict[supply_name]["parent"], "")
        self.parents.fill_from_input_line(mock_line)

    def change_condition_data(self):
        self.supply_dict[self.name]["condition"] = self.conditions.value.text()
        self.data_changed.emit()

    def change_parent_data(self):
        self.supply_dict[self.name]["parent"] =self.parents.value.text().split(",")
        self.data_changed.emit()


class DiscountView(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.secondary_layout = QHBoxLayout()
        self.values_layout = QVBoxLayout()
        self.props_layout = QVBoxLayout()
        self.secondary_layout.addLayout(self.values_layout)
        self.secondary_layout.addLayout(self.props_layout)
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font: bold 16px;")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.conditions = SimpleView()
        self.conditions.value_changed.connect(self.change_data)
        self.parents = SimpleView()
        self.parents.value_changed.connect(self.change_parent_data)
        # self.buy_discount = SimpleView()
        # self.buy_discount.value_changed.connect(self.change_buy_data)
        # self.buy_discount.value.setFixedWidth(100)
        # self.sell_discount = SimpleView()
        # self.sell_discount.value_changed.connect(self.change_sell_data)
        # self.sell_discount.value.setFixedWidth(100)
        self.main_layout.addWidget(self.name_label)
        # self.values_layout.addWidget(self.buy_discount)
        # self.values_layout.addWidget(self.sell_discount)
        self.props_layout.addWidget(self.parents)
        self.props_layout.addWidget(self.conditions)
        self.main_layout.addLayout(self.secondary_layout)
        self.setLayout(self.main_layout)

        self.trade_data = None
        self.index = None

    def set_data(self, trade_data, index):
        self.trade_data = trade_data
        self.index = index
        self.name_label.setText("Discount " + str(self.index + 1))
        mock_line = LineEntry("", 0, "", "Name", [self.trade_data["line"].value[self.index]], "")
        self.parents.fill_from_input_line(mock_line)
        mock_line = LineEntry("", 0, "", "Conditions", [self.trade_data["line"].conditions[self.index]], "")
        self.conditions.fill_from_input_line(mock_line)
        # entry = self.trade_data["entries"][self.trade_data["line"].value[self.index]]
        # mock_line = LineEntry("", 0, "", "Buy discount", entry.properties["buy"].value, "")
        # self.buy_discount.fill_from_input_line(mock_line)
        # mock_line = LineEntry("", 0, "", "Sell discount", entry.properties["sell"].value, "")
        # self.sell_discount.fill_from_input_line(mock_line)

    def change_data(self):
        self.line_entry.conditions[self.index] = self.conditions.value.text()
        self.data_changed.emit()

    def change_parent_data(self):
        self.line_entry.value[self.index] = self.parents.value.text()
        self.data_changed.emit()

    def change_buy_data(self):
        pass

    def change_sell_data(self):
        pass