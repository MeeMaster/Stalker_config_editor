import sys

from PyQt5.QtWidgets import QApplication

from description_reader import translated_descriptions, read_descriptions
from entry_classes import CraftingEntry
from file_reader import *
from window import MainWindow
from images import *
from constants import sections, tools


class DataHandler:
    def __init__(self):
        self.names = {}
        self.descriptions = {}
        self.item_name_xml_dict = {}
        self.dict = {}
        self.entries = {}
        self.item_types = {}
        self.item_groups = {}
        self.files = {}
        self.grouped_name_dict = {}

    def reset(self):
        self.names = {}
        self.descriptions = {}
        self.item_name_xml_dict = {}
        self.dict = {}
        self.entries = {}
        self.item_types = {}
        self.item_groups = {}
        self.files = {}
        self.grouped_name_dict = {}

    def get_all_item_properties(self, item):
        fetched_entries = {}

        def get_parent_data(parent_item, level=1):
            parents = self.entries[parent_item].parents
            if level not in fetched_entries:
                fetched_entries[level] = {}
            if parents is None:
                return
            for parent in parents:
                if parent not in self.entries:
                    continue
                new_dict = self.entries[parent]
                for entry in new_dict.properties:
                    fetched_entries[level][entry] = new_dict.properties[entry]
                get_parent_data(parent, level + 1)

        get_parent_data(item)

        for level in sorted(fetched_entries.keys(), reverse=True):
            for entry in fetched_entries[level]:
                if entry in self.entries[item].properties and level >= self.entries[item].properties[entry].level:
                    continue
                self.entries[item].properties[entry] = fetched_entries[level][entry]
                self.entries[item].properties[entry].level = level

        if self.entries[item].has_property("hit_absorbation_sect"):
            sect = self.entries[item].properties["hit_absorbation_sect"].value[0]
            level = self.entries[item].properties["hit_absorbation_sect"].level
            for entry in self.entries[sect].properties:
                if entry in self.entries[item].properties and level >= self.entries[item].properties[entry].level:
                    continue
                self.entries[item].properties[entry] = self.entries[sect].properties[entry]
                self.entries[item].properties[entry].level = level + 1

        if self.entries[item].has_property("immunities_sect"):
            sect = self.entries[item].properties["immunities_sect"].value[0]
            level = self.entries[item].properties["immunities_sect"].level
            for entry in self.entries[sect].properties:
                if entry in self.entries[item].properties and level >= self.entries[item].properties[entry].level:
                    continue
                self.entries[item].properties[entry] = self.entries[sect].properties[entry]
                self.entries[item].properties[entry].level = level + 1

    def load_all_files(self, dirpath):
        self.load_all_configs(dirpath)
        item_groups, item_types = get_item_types(dirpath)
        for item_group_name, item in item_groups.items():
            self.item_groups[item_group_name] = item
        for item_types_name, item in item_types.items():
            self.item_types[item_types_name] = item
        read_descriptions(dirpath, self.entries)
        self.get_descriptions()
        self.get_all_items_data()
        self.get_grouped_name_dict()
        load_all_icons()

    def read_trade_info(self, dirpath):

        pass

    def get_descriptions(self):
        self.names = translated_names
        self.descriptions = translated_descriptions

    def load_all_configs(self, dirpath):
        files = read_all_files(dirpath)
        file_entry = read_items(dirpath)
        if file_entry is not None:
            self.files[file_entry.path] = file_entry
        for filename, file_entry in files.items():
            self.files[filename] = file_entry

        self.entries = self.get_all_entries()

    def get_entries_from_file(self, file_entry):
        entries = {}
        for index, entry in file_entry.entries_order.items():
            entries[entry.name] = entry
        return entries

    def get_all_entries(self):
        all_entries = {}
        for filename, file_entry in self.files.items():
            entries = self.get_entries_from_file(file_entry)
            for entry_name, entry in entries.items():
                all_entries[entry_name] = entry
        return all_entries

    def get_items_with_prop(self, prop):
        return [entry for name, entry in self.entries.items() if entry.has_property(prop)]

    def get_item(self, item_name):
        return self.entries[item_name] if item_name in self.entries else None

    def get_items(self, items):
        return [self.entries[name] for name in items if name in self.entries]

    def get_all_item_data(self, name):
        self.get_all_item_properties(name)
        item_dict = self.entries[name]
        return item_dict

    def change_item_value(self, name, prop_name, new_value):
        self.entries[name].change_value(prop_name, new_value)

    def get_item_name(self, item):
        name_tag = self.item_name_xml_dict[item][0] if item in self.item_name_xml_dict else None
        if name_tag is None:
            return item
        return translated_names[name_tag] if name_tag in translated_names else None

    def get_grouped_name_dict(self):
        self.grouped_name_dict = get_grouped_name_dict(self.item_types)
        for item_type, items in self.grouped_name_dict.items():
            for item_translated, entry_name in items:
                if entry_name not in self.entries:
                    continue
                self.entries[entry_name].set_category(item_type)

    def get_all_items_data(self):
        for entry in self.entries:
            self.get_all_item_properties(entry)

    def write_all(self, dirpath):
        write_all(self.files, dirpath)

    def read_gamedata(self, dirpath):
        if not self.files:
            return
        self.load_all_files(dirpath)

    def get_items_of_type(self, type_name):
        return [entry for name, entry in self.entries.items() if entry.has_parent(type_name)]

    def get_crafting_recipes(self,  name_tag):
        entry_lines = []
        for craft_type in range(1, 7):
            for item_name in self.entries[str(craft_type)].properties:
                if name_tag == item_name[2:]:
                    entry_lines.append(self.entries[str(craft_type)].properties[item_name])
        return entry_lines

    def remove_line(self, entry_name, line_name):
        if entry_name not in self.entries:
            return
        if line_name not in self.entries[entry_name].properties:
            return
        del self.entries[entry_name].properties[line_name]
        self.entries[entry_name].changed = True

    def add_line(self, entry_name, line):
        if entry_name not in self.entries:
            return
        self.entries[entry_name].properties[line.prop] = line.copy()
        self.entries[entry_name].changed = True

    def get_craft_info(self, name_tag):
        disassembly = {}
        is_conditional = "false"
        conditional = self.entries["con_parts_list"]
        if name_tag in conditional.properties:
            is_conditional = "true"
            for entry in self.get_items(conditional.properties[name_tag].value):
                craft_entry = CraftingEntry()
                craft_entry.fixed_quantity = True
                craft_entry.set_entry(entry)
                disassembly[entry.name] = craft_entry

        unconditional = self.entries["nor_parts_list"]
        if name_tag in unconditional.properties:
            for entry in self.get_items(unconditional.properties[name_tag].value):
                if entry.name in disassembly:
                    disassembly[entry.name].add()
                    continue
                craft_entry = CraftingEntry()
                craft_entry.set_entry(entry)
                disassembly[entry.name] = craft_entry

        crafting = {}
        final_craft_type = None
        for craft_type in range(1, 7):
            for item_name in self.entries[str(craft_type)].properties:
                if name_tag == item_name[2:]:
                    craft_dict = {"craft_requirements": None, "entries": {}}
                    final_craft_type = craft_type
                    crafting_line = list(self.entries[str(craft_type)].properties[item_name].value)
                    toolkit = int(crafting_line.pop(0))
                    toolkit = self.get_item(tools[toolkit])
                    toolkit_entry = CraftingEntry()
                    toolkit_entry.load_from_entry(toolkit)
                    toolkit_entry.quantity = 1

                    rec_entry = self.get_item(crafting_line.pop(0))
                    if rec_entry is not None:
                        required_recipe = CraftingEntry()
                        required_recipe.load_from_entry(rec_entry)
                        required_recipe.quantity = 1
                    else:
                        required_recipe = None
                    craft_dict["craft_requirements"] = (toolkit_entry, required_recipe)
                    while crafting_line:
                        item = self.get_item(crafting_line.pop(0))
                        craft_entry = CraftingEntry()
                        craft_entry.set_entry(item)
                        item_quantity = crafting_line.pop(0)
                        craft_entry.quantity = int(item_quantity)
                        craft_dict["entries"][craft_entry.name] = craft_entry
                    crafting[item_name] = craft_dict
        return {"item": name_tag, "craft_type": final_craft_type, "craft": crafting,
                "disassemble": disassembly, "conditional": is_conditional}


class App:
    def __init__(self):
        self.main_window = MainWindow()
        self.main_widget = self.main_window.window_widget
        self.data_handler = DataHandler()
        self.item_dataframes = {}
        self.current_item = None
        self.current_tab = 0

        # Register signals
        # Register directory selection signal
        self.main_window.directory_signal.connect(self.read_files)
        # Register item selection signal
        self.main_widget.item_signal.connect(self.display_data_for_item)
        # Register section change signal
        self.main_widget.section_signal.connect(self.change_section)
        # Register value change signal
        self.main_widget.value_changed.connect(self.change_value)
        # Register fill request
        self.main_widget.fill_request.connect(self.fill_window)
        # Register tab change
        self.main_widget.tab_change.connect(self.change_tab)
        # Register crafting update
        self.main_widget.craft_update.connect(self.update_crafting)

    def update_crafting(self, crafting_dict):
        craft_lines = self.data_handler.get_crafting_recipes(self.current_item)

        for craft_line in craft_lines:
            if craft_line.prop not in crafting_dict["craft"]:
                self.data_handler.remove_line(craft_line.name, craft_line.prop)

        mock_craft_line = LineEntry(file=self.data_handler.entries["1"].file,
                                    lineno=-1,
                                    name="",
                                    prop="",
                                    value=[],
                                    comment="")

        for entry_name in crafting_dict["craft"]:
            if not crafting_dict["craft"][entry_name]["entries"]:
                continue
            mock_line = mock_craft_line.copy()
            mock_line.name = str(crafting_dict["craft_type"])
            mock_line.prop = entry_name
            booklet = crafting_dict["craft"][entry_name]["craft_requirements"][1]
            if booklet is None:
                booklet = "recipe_basic_0"
            else:
                booklet = booklet.name
            toolkit = crafting_dict["craft"][entry_name]["craft_requirements"][0]
            if toolkit is None:
                toolkit = "itm_basickit"
            else:
                toolkit = [key for key, value in tools.items() if value == toolkit.name][0]
            mock_line.value = [str(toolkit), booklet]
            for entry_n, entry in crafting_dict["craft"][entry_name]["entries"].items():
                mock_line.value.append(entry_n)
                mock_line.value.append(str(entry.quantity))
            self.data_handler.add_line(mock_line.name, mock_line)  # adds or replaces the line

        if not crafting_dict["disassemble"]:
            return
        mock_craft_line = LineEntry(file=self.data_handler.entries["con_parts_list"].file,
                                    lineno=-1,
                                    name="",
                                    prop="",
                                    value=[],
                                    comment="")
        entry_name = "con_parts_list" if crafting_dict["conditional"] == "true" else "nor_parts_list"
        mock_craft_line.name = entry_name
        if self.current_item in self.data_handler.entries["con_parts_list"].properties:
            self.data_handler.remove_line("con_parts_list", self.current_item)
        if self.current_item in self.data_handler.entries["nor_parts_list"].properties:
            self.data_handler.remove_line("nor_parts_list", self.current_item)
        mock_craft_line.prop = self.current_item
        for part_name, part in crafting_dict["disassemble"].items():
            mock_craft_line.value.extend([part_name] * part.quantity)
        self.data_handler.add_line(mock_craft_line.name, mock_craft_line)

    def display_data_for_item(self, item_tag):
        self.current_item = item_tag

        item_dict = self.data_handler.get_all_item_data(item_tag)
        self.main_widget.display_value_data(item_dict)
        crafting_info = self.data_handler.get_craft_info(item_tag)
        self.main_widget.craft_view.fill_values(crafting_info)
        self.main_widget.icon_widget.load_entry(item_dict)

    def change_tab(self, index):
        self.current_tab = index
        if not self.data_handler.entries:
            return
        if self.current_tab in [0, 1]:
            self.main_widget.set_combo_options(["Ammo", "Armor", "Artifacts", "Consumables",
                                                "Devices", "Tools", "Weapons", "Other"])
        else:
            self.main_widget.set_combo_options([])

    def fill_window(self, window, name, data_type):  ### TODO: Fix this so that the signal comes from particular gridview, not the entire popup
        if data_type == "prop":
            all_entries = []
            for n in name:
                entries = self.data_handler.get_items_with_prop(n)
                all_entries += entries
            window.set_available_entries(all_entries)
        elif data_type == "name":
            entries = self.data_handler.get_items(name)
            window.set_selected_entries(entries)
        elif data_type == "type":
            all_entries = []
            for n in name:
                entries = self.data_handler.get_items_of_type(n)
                all_entries += entries
            window.set_available_entries(all_entries)

    def change_value(self, entry_name, new_value):
        self.data_handler.change_item_value(self.current_item, entry_name, new_value)
        self.main_widget.icon_widget.load_entry(self.data_handler.get_item(self.current_item))

    def read_files(self, dirpath, read):
        if read == "read":
            self.data_handler.reset()
            self.data_handler.load_all_files(dirpath)
            if self.current_tab in [0, 1]:
                self.main_widget.set_combo_options(["Ammo", "Armor", "Artifacts", "Consumables",
                                "Devices", "Tools", "Weapons", "Other"])
        elif read == "write":
            self.write_all_files(dirpath)
        elif read == "gamedata":
            self.data_handler.read_gamedata(dirpath)

    def display_item_list(self, item_dict):
        self.main_widget.display_item_list(item_dict)

    def write_all_files(self, dirpath):
        self.data_handler.write_all(dirpath)

    def change_section(self, current_section):
        all_items = self.data_handler.grouped_name_dict
        current_dict = {}
        target_parts = []
        if current_section in sections:
            target_parts = sections[current_section]
        for part in target_parts:
            if part not in all_items:
                continue
            current_dict[part] = all_items[part]
        self.display_item_list(current_dict)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_class = App()
    app_class.read_files("E:/Stalker_modding/unpacked", "read")
    sys.exit(app.exec_())

