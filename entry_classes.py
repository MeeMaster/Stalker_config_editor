import os

credit_line = ";Created using Anomaly config editor. For more info visit www.moddb.com/mods/stalker-anomaly/addons/config-editor/"


class FileEntry:

    def __init__(self, path):
        self.path = path
        self.header = []
        self.entries_order = {}

    def is_changed(self):
        for index, entry in self.entries_order.items():
            if entry.is_changed():
                return True
        return False

    def write_file_entry(self, dirpath: str):
        from file_reader import split_all
        path = os.path.join(*split_all(dirpath), self.path)
        subfolders = split_all(os.path.split(path)[0])
        for index, subfolder in enumerate(subfolders):
            if not os.path.exists(os.path.join(*subfolders[:index+1])):
                os.mkdir(os.path.join(*subfolders[:index+1]))
        with open(path, "w", encoding="ISO-8859-1") as outfile:
            if not self.header or self.header[0] != credit_line:
                self.header.insert(0, credit_line)
            outfile.write("\n".join(self.header))
            for order, entry in sorted(self.entries_order.items(), key=lambda x: x[0]):
                outfile.write("\n\n")
                outfile.write(entry.write())


class LineEntry:
    def __init__(self, file, lineno, name, prop, value, conditions=[], comment=""):
        self.file = file.strip()
        self.lineno = lineno
        self.name = name.strip()
        self.prop = prop.strip()
        # self.parent = parent
        self.value = value
        self.default = value
        self.comment = comment.strip()
        self.level = 0
        self.equal_sign = True
        self.conditions = conditions
        self.changed = False

    def __repr__(self):
        return "{}: {}".format(self.prop, ",".join(self.value))

    def tolist(self):
        return [self.file, self.lineno, self.name, self.prop, self.value, self.comment]

    def copy(self):
        new_entry = LineEntry(str(self.file), int(self.lineno), str(self.name), str(self.prop),
                              list(self.value), list(self.conditions), str(self.comment))
        new_entry.default = list(self.default)
        return new_entry

    def write(self):
        print(self.value, len(self.value), self.conditions)
        line = "\t\t{}{}{} {}\t{}".format(self.prop,
                                          "\t" * (10 - (len(self.prop) // 4)),
                                          "=" if self.equal_sign else "",
                                          ",".join([" ".join([self.conditions[index], self.value[index]])
                                                    for index in range(len(self.value))]) if self.value else "",
                                          (";" if self.comment else "") + self.comment)
        return line

    def is_changed(self):
        if self.changed:
            return True
        if self.value != self.default:
            return True
        return False


class Entry:
    def __init__(self):
        self.name = None
        self.parents = None
        self.file = None
        self.start_line = None
        self.translation = None
        self.description = None
        self.entry_type = None
        self.properties = {}
        self.comment_lines = {}
        self.changed = False
        self.category = None
        self.is_item = False

    def reset_parents(self):
        for prop_name, prop in list(self.properties.items()):
            if prop.name != self.name:
                del self.properties[prop_name]

    def load_data(self, name, parents, filename, start_line):
        self.name = name
        self.parents = parents
        self.file = filename
        self.start_line = start_line

    def load_from_entry(self, entry):
        self.name = entry.name
        self.parents = entry.parents
        self.file = entry.file
        self.start_line = entry.start_line
        self.translation = entry.translation
        self.description = entry.description
        self.entry_type = entry.entry_type
        self.properties = entry.properties
        self.comment_lines = entry.comment_lines
        self.category = entry.category

    def __repr__(self):
        return "Entry: {}".format(self.name)  # response

    def set_parents(self, parents):
        self.parents = parents

    def change_value(self, property_name, new_value):
        for prop_name, prop in self.properties.items():
            if prop_name != property_name:
                continue
            self.properties[prop_name] = prop.copy()
            self.properties[prop_name].value = new_value.split(",")
            if self.properties[prop_name].name != self.name:
                if self.properties[prop_name].name.endswith("_absorbation") or\
                        self.properties[prop_name].name.endswith("_immunities"):
                    if "_base" not in self.properties[prop_name].name:
                        continue
                self.properties[prop_name].name = self.name
                self.properties[prop_name].lineno = -1
                self.properties[prop_name].file = self.file

    def set_category(self, category):
        self.category = category
        self.is_item = True

    def determine_category(self):
        self.category = self.get_item_type()

    def has_property(self, prop):
        return prop in self.properties

    def is_category(self, category):
        return self.category == category

    def is_artifact(self):
        for entry in self.properties:
            if self.properties[entry].name == "af_base":
                return True
        return False

    def is_armor(self):
        for entry in self.properties:
            if self.properties[entry].name == "outfit_actions" or self.properties[entry].name == "outfit_base":
                return True
        return False

    def is_weapon(self):
        for entry in self.properties:
            if self.properties[entry].name == "default_weapon_params":
                return True
        return False

    def is_food(self):
        is_booster = False
        is_repair = False
        for entry in self.properties:
            if self.properties[entry].name == "booster":
                is_booster = True
            if self.properties[entry].name == "tch_repair":
                is_repair = True
        return is_booster and not is_repair

    def is_repair(self):
        is_booster = False
        is_repair = False
        for entry in self.properties:
            if self.properties[entry].name == "booster":
                is_booster = True
            if self.properties[entry].name == "tch_repair":
                is_repair = True
        return is_booster and is_repair

    def is_ammo(self):
        for entry in self.properties:
            if self.properties[entry].name == "ammo_base":
                return True
        return False

    def is_device(self):
        for entry in self.properties:
            if self.properties[entry].name == "tch_device":
                return True
        return False

    def get_item_type(self):
        if self.is_repair():
            return "repair"
        if self.is_artifact():
            return "artifact"
        if self.is_armor():
            return "armor"
        if self.is_food():
            return "food"
        if self.is_ammo():
            return "ammo"
        if self.is_weapon():
            return "weapon"
        if self.is_device():
            return "device"
        return "base"

    def has_parent(self, parent):
        for line_name, line_entry in self.properties.items():
            if line_entry.name == parent:
                return True
        return False

    def get_last_line(self):
        return max([line_entry.lineno for line_name, line_entry in self.properties.items()] +
                   list(self.comment_lines.keys()))

    def write(self):
        lines = {}
        added_lines = []
        for line_name, line_entry in self.properties.items():
            line_no = line_entry.lineno
            if line_no == -1:
                added_lines.append(line_entry)
                continue
            if line_entry.name != self.name:
                continue
            lines[line_no] = line_entry
        for line_no, comment in self.comment_lines.items():
            lines[line_no] = comment

        output = []
        entry_name = "[{}]".format(self.name)
        if self.parents is not None:
            entry_name += ":{}".format(",".join(self.parents))
        output.append(entry_name)
        for line_no in sorted(lines.keys()):
            entry = lines[line_no]
            if not isinstance(entry, LineEntry):
                output.append(entry)
                continue
            output.append(entry.write())

        if added_lines:
            output.append("; Added properties")
            for entry in added_lines:
                output.append(entry.write())
            output.append(";;--==========================================================================")
        return "\n".join(output)

    def is_changed(self):
        if self.changed:
            return True
        for name, prop in self.properties.items():
            if prop.value != prop.default or prop.lineno < 0 or prop.changed:
                return True
        return False

    def todict(self):
        return {self.name: self}

    def from_entry(self, entry):
        self.load_from_entry(entry)
        return self


class CraftingEntry(Entry):

    def __init__(self):
        Entry.__init__(self)
        self.quantity = 0
        self.fixed_quantity = False

    def from_entry(self, entry):
        self.load_from_entry(entry)
        self.quantity = 1

    def add(self, value=1):
        print(value)
        if self.fixed_quantity:
            return
        self.quantity += value

    def remove(self, value=1):
        if self.fixed_quantity:
            return
        self.quantity -= value
        if self.quantity < 0:
            self.quantity = 0


class TradeEntry(CraftingEntry):

    def __init__(self):
        CraftingEntry.__init__(self)
        self.chance = {}
        self.quantity = {}
        self.buy_price = 1. #[1., 1.]
        self.sell_price = 1. #[1., 1.]

    def set_chance(self, supply, chance: float):
        self.chance[supply] = chance

    def from_entry(self, entry):
        self.load_from_entry(entry)
        self.quantity = {}
        return self

    def set_buy_price(self, price1: float):
        self.buy_price = price1
        # self.buy_price[1] = price2

    def set_sell_price(self, price1: float):
        self.sell_price = price1
        # self.sell_price[1] = price2

