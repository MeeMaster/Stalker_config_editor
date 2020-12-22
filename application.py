import sys

from PyQt5.QtWidgets import QApplication

from description_reader import translated_names, translated_descriptions, read_descriptions
from file_reader import *
from window import MainWindow
from images import *
from constants import sections


class DataHandler:
    def __init__(self):
        self.reset()

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
        self.item_groups, self.item_types = get_item_types(dirpath)
        read_descriptions(dirpath, self.entries)
        self.get_descriptions()
        self.get_all_items_data()
        load_all_icons()

    def get_descriptions(self):
        self.names = translated_names
        self.descriptions = translated_descriptions

    def load_all_configs(self, dirpath):
        files, entries = read_all_files(dirpath)
        for filename, file_entry in files.items():
            self.files[filename] = file_entry
        for entry_name, entry in entries.items():
            self.entries[entry_name] = entry
        file_entry, entries = read_items(dirpath)
        if file_entry is None or entries is None:
            return
        self.files[file_entry.path] = file_entry
        for entry_name, entry in entries.items():
            self.entries[entry_name] = entry

    def get_items_with_prop(self, prop):
        return [entry for name, entry in self.entries.items() if entry.has_property(prop)]

    def get_item(self, item_name):
        return self.entries[item_name] if item_name in self.entries else None

    def get_items(self, items):
        return [entry for name, entry in self.entries.items() if name in items]

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
        output_dict = get_grouped_name_dict(self.item_types)
        return output_dict

    def get_all_items_data(self):
        for entry in self.entries:
            self.get_all_item_properties(entry)

    def write_all(self, dirpath):
        write_all(self.files, dirpath)

    def read_gamedata(self, dirpath):
        if not self.files:
            return
        self.load_all_configs(dirpath)
        item_groups, item_types = get_item_types(dirpath)
        for item_group_name, item in item_groups.items():
            self.item_groups[item_group_name] = item
        for item_types_name, item in item_types.items():
            self.item_types[item_types_name] = item
        read_descriptions(dirpath, self.entries)
        self.get_descriptions()
        self.get_all_items_data()

    def reset(self):
        self.names = {}
        self.descriptions = {}
        self.item_name_xml_dict = {}
        self.dict = {}
        self.entries = {}
        self.item_types = {}
        self.item_groups = {}
        self.files = {}


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
        # Regiser tab change
        self.main_widget.tab_change.connect(self.change_tab)
        # Register save signal
        # self.main_window.save_data.connect(self.write_all_files)

    def display_data_for_item(self, item_tag):
        self.current_item = item_tag
        item_dict = self.data_handler.get_all_item_data(item_tag)
        self.main_widget.display_value_data(item_dict)
        # icon = load_icon_from_entry(item_dict)
        # name = translated_names[item_tag]
        self.main_widget.icon_widget.load_entry(item_dict)

    def change_tab(self, index):
        self.current_tab = index

    def fill_window(self, window, name, is_type):
        if is_type:
            entries = self.data_handler.get_items_with_prop(name)
            window.set_available_entries(entries)
        else:
            entries = self.data_handler.get_items(name.split(","))
            window.set_selected_entries(entries)

    def change_value(self, entry_name, new_value):
        self.data_handler.change_item_value(self.current_item, entry_name, new_value)
        self.main_widget.icon_widget.load_entry(self.data_handler.get_item(self.current_item))

    def read_files(self, dirpath, read):
        if read == "read":
            self.data_handler.reset()
            self.data_handler.load_all_files(dirpath)
        elif read == "write":
            self.write_all_files(dirpath)
        elif read == "gamedata":
            self.data_handler.read_gamedata(dirpath)

    def display_item_list(self, item_dict):
        self.main_widget.display_item_list(item_dict)

    def write_all_files(self, dirpath):
        self.data_handler.write_all(dirpath)

    def change_section(self, current_section):
        all_items = self.data_handler.get_grouped_name_dict()
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
    sys.exit(app.exec_())

