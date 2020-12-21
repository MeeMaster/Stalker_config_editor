import sys

from PyQt5.QtWidgets import QApplication

from description_reader import translated_names, translated_descriptions, read_descriptions
from file_reader import Reader
from window import MainWindow
from images import *


class DataHandler:
    def __init__(self):
        self.reader = Reader()
        self.names = {}
        self.descriptions = {}
        self.item_name_xml_dict = {}
        self.dict = {}
        # self.df = None

    def load_all_files(self, dirpath):
        self.reader.set_dirpath(dirpath)
        self.load_all_configs()
        self.reader.get_item_types()
        read_descriptions(dirpath, self.reader.entries)
        self.get_descriptions(dirpath)
        self.get_all_items_data()
        load_all_icons(dirpath)

    def get_descriptions(self, dirpath):
        self.names = translated_names
        self.descriptions = translated_descriptions

    def load_all_configs(self):
        self.reader.read_all_files()
        self.reader.read_items()

    def get_items_with_prop(self, prop):
        return [entry for name, entry in self.reader.entries.items() if entry.has_property(prop)]

    def get_item(self, item_name):
        return self.reader.entries[item_name] if item_name in self.reader.entries else None

    def get_items(self, items):
        return [entry for name, entry in self.reader.entries.items() if name in items]

    def get_all_item_data(self, name):
        self.reader.get_all_item_properties(name)
        item_dict = self.reader.entries[name]
        return item_dict

    def change_item_value(self, name, prop_name, new_value):
        self.reader.entries[name].change_value(prop_name, new_value)

    def get_item_name(self, item):
        name_tag = self.item_name_xml_dict[item][0] if item in self.item_name_xml_dict else None
        if name_tag is None:
            return item
        return translated_names[name_tag] if name_tag in translated_names else None

    def get_grouped_name_dict(self):
        output_dict = self.reader.get_grouped_name_dict()
        return output_dict

    def get_all_items_data(self):
        for entry in self.reader.entries:
            self.reader.get_all_item_properties(entry)

    def write_all(self, dirpath):
        self.reader.write_all(dirpath)


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
        if read:
            self.data_handler.load_all_files(dirpath)
        else:
            self.write_all_files(dirpath)

    def display_item_list(self, item_dict):
        self.main_widget.display_item_list(item_dict)

    def write_all_files(self, dirpath):
        self.data_handler.write_all(dirpath)

    def change_section(self, current_section):
        all_items = self.data_handler.get_grouped_name_dict()
        current_dict = {}
        if current_section == "Ammo":
            target_parts = ['ammo', 'ammo_bad', 'ammo_damaged']
        if current_section == "Armor":
            target_parts = ['headgear', 'outfits', 'outfits_ecolog']
        if current_section == "Artifacts":
            target_parts = ['artefacts', 'mutant_parts', 'artefacts_h']
        if current_section == "Consumables":
            target_parts = ['drugs', 'cigs', 'drinks', "food", "mutant_parts"]
        if current_section == "Devices":
            target_parts = ['devices', 'backpacks']
        if current_section == "Equipment":
            target_parts = ['headgear', 'outfits', 'outfits_ecolog']
        if current_section == "Tools":
            target_parts = ['tools', 'repair_kits', 'upgrade_items', "parts", "toolkits_h"]
        if current_section == "Weapons":
            target_parts = ['pistols', 'rifles', 'melee', "explosives"]
        if current_section == "Other":
            target_parts = ['money', 'camping', 'common_stock', "misc", "unused"]
        for part in target_parts:
            if part not in all_items:
                continue
            current_dict[part] = all_items[part]

        self.display_item_list(current_dict)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_class = App()
    sys.exit(app.exec_())

