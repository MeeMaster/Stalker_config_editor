import sys

from PyQt5.QtWidgets import QApplication, QErrorMessage
import configs
from description_reader import translated_descriptions, read_descriptions
from entry_classes import CraftingEntry, TradeEntry
from file_reader import *
from window import MainWindow
from images import *
from constants import basic_sections, sections, tools


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
        self.traders = {}

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
        self.traders = {}

    def get_all_item_properties(self, item):
        fetched_entries = {}
        if isinstance(item, str):
            item = self.entries[item]
        # item_data = self.entries[item]
        item.reset_parents()
        same_file_entries = {entry.name: entry for index, entry in self.files[item.file].entries_order.items()}

        def get_parent_data(parent_item, level=1):
            parents = parent_item.parents
            if level not in fetched_entries:
                fetched_entries[level] = {}
            if parents is None:
                return
            for parent in parents:
                if parent in same_file_entries:
                    new_dict = same_file_entries[parent]
                elif parent in self.entries:
                    new_dict = self.entries[parent]
                else:
                    continue
                for entry in new_dict.properties:
                    fetched_entries[level][entry] = new_dict.properties[entry]
                get_parent_data(new_dict, level + 1)

        get_parent_data(item)
        for level in sorted(fetched_entries.keys(), reverse=True):
            for entry in fetched_entries[level]:
                if entry in item.properties and level >= item.properties[entry].level:
                    continue
                item.properties[entry] = fetched_entries[level][entry]
                item.properties[entry].level = level

        if item.has_property("hit_absorbation_sect"):
            sect = item.properties["hit_absorbation_sect"].value[0]
            level = item.properties["hit_absorbation_sect"].level
            if sect in self.entries:
                for entry in self.entries[sect].properties:
                    if entry in item.properties and level >= item.properties[entry].level:
                        continue
                    item.properties[entry] = self.entries[sect].properties[entry]
                    item.properties[entry].level = level + 1

        if item.has_property("immunities_sect"):
            sect = item.properties["immunities_sect"].value[0]
            level = item.properties["immunities_sect"].level
            if sect in self.entries:
                for entry in self.entries[sect].properties:
                    if entry in item.properties and level >= item.properties[entry].level:
                        continue
                    item.properties[entry] = self.entries[sect].properties[entry]
                    item.properties[entry].level = level + 1
        return item

    def file_present(self, filename):
        if ".ltx" not in filename:
            filename = filename+".ltx"
        for full_file_name in self.files:
            file_name = os.path.split(full_file_name)[1]
            if file_name == filename:
                return True
        return False

    def crafting_available(self):
        if "con_parts_list" not in self.entries or \
                "nor_parts_list" not in self.entries or \
                not self.file_present("craft"):
            return False
        return True

    def get_items_with_category(self, category):
        return [entry for entry_name, entry in self.entries.items() if entry.category == category and entry.is_item]

    def load_all_files(self, dirpath, debug=False):
        self.load_all_configs(dirpath)
        item_groups, item_types = get_item_types(dirpath)

        if item_groups is None or item_types is None:
            self.item_types = None
            self.item_groups = None
        else:
            for item_group_name, item in item_groups.items():
                self.item_groups[item_group_name] = item
            for item_types_name, item in item_types.items():
                self.item_types[item_types_name] = item
        self.get_all_items_data()
        read_descriptions(dirpath, self.entries)
        self.get_descriptions()
        if self.item_types is not None:
            self.get_grouped_name_dict()
        else:
            self.determine_items()
        self.get_all_item_names()
        if debug:
            return
        load_all_icons()

    def get_all_item_names(self):
        for entry_name, entry in self.entries.items():
            trans_name = translated_names[entry_name] if entry_name in translated_names else entry_name
            entry.translation = trans_name

    def determine_items(self):
        for entry_name, entry in self.entries.items():
            if entry.has_property("inv_name"):
                entry.is_item = True
                entry.determine_category()

    def get_traders(self):
        trader_names = []
        traders = {}
        for filename, file_entry in self.files.items():
            if "trade" not in filename:
                continue
            entries = {}
            for index, entry in file_entry.entries_order.items():
                entries[entry.name] = entry
            if "trader" not in entries:
                continue
            name = os.path.splitext(os.path.split(filename)[1])[0].replace("trade_", "")
            trader_names.append(name)
        for trader in trader_names:
            trade_info = self.get_trade_info(trader)
            if trade_info is None:
                continue
            traders[trader] = trade_info
        self.traders = traders

    def get_trade_info(self, trader):
        file_entry = None
        for filename, f_entry in self.files.items():
            name = os.path.splitext(os.path.split(filename)[1])[0].replace("trade_", "")
            if trader != name:
                continue
            file_entry = f_entry
        entries = {}
        for index, entry in file_entry.entries_order.items():
            entries[entry.name] = entry
        all_items = {}
        for entry_name, entry in self.entries.items():
            if entry.category is None:
                continue
            entry = TradeEntry().from_entry(entry)
            all_items[entry_name] = entry
        buy_cond = entries["trader"].properties["buy_condition"]
        sell_cond = entries["trader"].properties["sell_condition"]
        if "buy_supplies" not in entries["trader"].properties:
            return None
        trade_entry = {"Trader": trader,
                       "Merch": all_items,
                       "Stocks": {},
                       "Stock_info": {},
                       "Stock_line": entries["trader"].properties["buy_supplies"],
                       "Buy_conditions":  entries[buy_cond.value[0]],
                       "Sell_conditions": entries[sell_cond.value[0]],  # TODO: Add custom buy/sell conditions!!
                       "discounts": entries["trader"].properties["discounts"] if
                       "discounts" in entries["trader"].properties else LineEntry("", 0, "", "discounts", []),
                       "buy_item_condition_factor": entries["trader"].properties["buy_item_condition_factor"] if
                       "buy_item_condition_factor" in entries["trader"].properties else None,
                       "buy_item_exponent": entries["trader"].properties["buy_item_exponent"] if
                       "buy_item_exponent" in entries["trader"].properties else None,
                       "sell_item_exponent": entries["trader"].properties["sell_item_exponent"] if
                       "sell_item_exponent" in entries["trader"].properties else None,
                       "buy_condition": buy_cond,
                       "sell_condition": sell_cond
                       }
        for index, values in enumerate(reversed(list(zip(entries["trader"].properties["buy_supplies"].value,
                                                         entries["trader"].properties["buy_supplies"].conditions)))):
            value, condition = values
            if not value:
                continue
            stock = entries[value]
            self.get_all_item_properties(stock)
            if not value:
                continue
            # stock = entries[value]
            # self.entries[value] = stock
            trade_entry["Stocks"][value] = stock
            trade_entry["Stock_info"][value] = {"condition": condition,
                                                "parent": stock.parents}
        return trade_entry

    def update_trader(self, trader):
        trade_data = self.get_trade_info(trader)
        self.traders[trader] = trade_data

    def get_descriptions(self):
        self.names = translated_names
        self.descriptions = translated_descriptions

    def load_all_configs(self, dirpath):
        files = read_all_files(dirpath)
        for filename, file_entry in files.items():
            if filename in self.files:
                del self.files[filename]
            self.files[filename] = file_entry

        all_entries = self.get_all_entries()
        for entry_name, entry in all_entries.items():
            if entry_name in self.entries:
                # continue
                del self.entries[entry_name]
            self.entries[entry_name] = entry

    def get_all_entries(self):
        all_entries = {}
        for filename, file_entry in self.files.items():
            entries = get_entries_from_file(file_entry)
            for entry_name, entry in entries.items():
                if entry_name in all_entries:
                    continue
                all_entries[entry_name] = entry
        return all_entries

    def get_file(self, filename):
        if ".ltx" not in filename:
            filename = filename + ".ltx"
        for file_name in self.files:
            if os.path.split(file_name)[1] == filename:
                return self.files[file_name]
        return None

    def get_items_with_prop(self, prop):
        return [entry for name, entry in self.entries.items() if entry.has_property(prop)]

    def get_item(self, item_name):
        return self.entries[item_name] if item_name in self.entries else None

    def get_items(self, items):
        return [self.entries[name] for name in items if name in self.entries]

    def get_all_item_data(self, name):
        item_data = self.get_all_item_properties(name)
        return item_data

    def change_item_value(self, name, prop_name, new_value):
        self.entries[name].change_value(prop_name, new_value)

    def get_grouped_name_dict(self):
        self.grouped_name_dict = get_grouped_name_dict(self.item_types)
        for item_type, items in self.grouped_name_dict.items():
            for item_translated, entry_name in items:
                if entry_name not in self.entries:
                    continue
                self.entries[entry_name].set_category(item_type)

    def get_all_items_data(self):
        for entry in self.entries:
            item_data = self.get_all_item_properties(entry)
            self.entries[item_data.name] = item_data

    def write_all(self, dirpath):
        write_all(self.files, dirpath)

    def read_gamedata(self, dirpath, debug=False):
        if not self.files:
            return "Read unpacked database first!"
        self.load_all_files(dirpath, debug)
        return False

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
                craft_entry.from_entry(entry)
                disassembly[entry.name] = craft_entry

        unconditional = self.entries["nor_parts_list"]
        if name_tag in unconditional.properties:
            for entry in self.get_items(unconditional.properties[name_tag].value):
                if entry.name in disassembly:
                    disassembly[entry.name].add()
                    continue
                craft_entry = CraftingEntry()
                craft_entry.from_entry(entry)
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
                        craft_entry.from_entry(item)
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
        # self.traders = []
        self.current_item = None
        self.current_tab = 0
        self.craft_available = False
        self.current_trader = None

        # Register signals
        # Register directory selection signal
        self.main_window.directory_signal.connect(self.read_files)
        # Register new icons
        self.main_window.icon_signal.connect(self.read_icons)
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
        # Register trade change upgrade
        self.main_widget.trade_update.connect(self.update_trade)

    def read_icons(self, filepath):
        load_equipment_icons(filepath)

    def update_trade(self, trade_info):
        trader = "trade_" + trade_info["Trader"]
        file_entry = self.data_handler.get_file(trader)
        # changed = False
        if file_entry is None:
            print("No such file!")
            return
        all_file_entries = {entry.name: entry for index, entry in file_entry.entries_order.items()}
        for supply_name in trade_info["Stock_info"]:
            if supply_name not in all_file_entries:
                continue
            entry = all_file_entries[supply_name]
            new_parents = trade_info["Stock_info"][supply_name]["parent"]
            if new_parents != entry.parents:
                entry.parents = new_parents
                entry.changed = True
                self.data_handler.update_trader(self.current_trader)
                trade_data = self.data_handler.traders[self.current_trader]
                self.main_widget.trade_view.set_data(trade_data)

    def update_crafting(self, crafting_dict):
        craft_lines = self.data_handler.get_crafting_recipes(self.current_item)

        for craft_line in craft_lines:
            if craft_line.prop not in crafting_dict["craft"]:
                self.data_handler.remove_line(craft_line.name, craft_line.prop)

        mock_craft_line = LineEntry(file=self.data_handler.entries["1"].file,
                                    lineno=-1,
                                    name="",
                                    prop="",
                                    value=[]
                                    )

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
                                    value=[]
                                    )
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
        if self.craft_available:
            crafting_info = self.data_handler.get_craft_info(item_tag)
            self.main_widget.craft_view.fill_values(crafting_info)
        self.main_widget.icon_widget.load_entry(item_dict)

    def change_tab(self, index):
        current_tab = int(self.current_tab)
        self.current_tab = index
        if not self.data_handler.entries:
            return
        self.set_combos(current_tab)

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

    def change_value(self):  # , entry_name, new_value):
        self.main_widget.icon_widget.load_entry(self.data_handler.get_item(self.current_item))

    def read_files(self, dirpath, read):
        if read == "read":
            self.data_handler.reset()
            self.data_handler.load_all_files(dirpath)
            self.set_combos()
        elif read == "write":
            self.write_all_files(dirpath)
            return
        elif read == "gamedata":
            error = self.data_handler.read_gamedata(dirpath)
            if error:
                self.raise_error(error)
        self.data_handler.get_traders()
        self.craft_available = self.data_handler.crafting_available()
        self.main_widget.tabs.setTabEnabled(1, self.craft_available)

    def set_combos(self, current_tab=None):
        if self.current_tab in [0, 1]:
            self.main_widget.disable_list(False)
            if current_tab in [0, 1]:
                return
            self.main_widget.set_combo_options(["Ammo", "Armor", "Artifacts", "Consumables",
                                                "Devices", "Tools", "Weapons", "Other"])
        elif self.current_tab in [2]:
            self.main_widget.disable_list(True)
            self.main_widget.set_combo_options(list(self.data_handler.traders.keys()))

    def display_item_list(self, item_dict):
        self.main_widget.display_item_list(item_dict)

    def raise_error(self, text):
        error_dialog = QErrorMessage()
        error_dialog.showMessage(text)

    def write_all_files(self, dirpath):
        self.data_handler.write_all(dirpath)

    def change_section(self, current_section):
        if self.current_tab in [0, 1]:
            all_items = self.data_handler.grouped_name_dict
            current_dict = {}
            target_parts = []
            if all_items:

                configs.basic_view = False
                if current_section in sections:
                    target_parts = sections[current_section]
                for part in target_parts:
                    if part not in all_items:
                        continue
                    current_dict[part] = all_items[part]
            else:
                configs.basic_view = True
                target_categories = []
                if current_section in basic_sections:
                    target_categories = basic_sections[current_section]
                for part in target_categories:
                    items = self.data_handler.get_items_with_category(part)
                    current_dict[part] = [(entry.translation, entry.name) for entry in items]
            self.display_item_list(current_dict)
        elif self.current_tab == 2:
            if not current_section:
                return
            self.current_trader = current_section
            trade_data = self.data_handler.traders[current_section]
            self.main_widget.trade_view.set_data(trade_data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_class = App()
    # app_class.read_files("E:/Stalker_modding/unpacked", "read")
    sys.exit(app.exec_())

