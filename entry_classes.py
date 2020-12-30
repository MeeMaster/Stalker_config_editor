import os


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
            outfile.write("\n".join(self.header))
            for order, entry in sorted(self.entries_order.items(), key=lambda x: x[0]):
                outfile.write("\n\n")
                outfile.write(entry.write())


class LineEntry:
    def __init__(self, file, lineno, name, prop, value, comment):
        self.file = file.strip()
        self.lineno = lineno
        self.name = name.strip()
        self.prop = prop.strip()
        # self.parent = parent
        self.value = value
        self.default = value
        self.comment = comment.strip()
        self.level = 0

    def __repr__(self):
        return "{}: {}".format(self.prop, ",".join(self.value))

    def tolist(self):
        return [self.file, self.lineno, self.name, self.prop, self.value, self.comment]

    def copy(self):
        new_entry = LineEntry(str(self.file), int(self.lineno), str(self.name), str(self.prop),
                              list(self.value), str(self.comment))
        new_entry.default = list(self.default)
        return new_entry

    def write(self):
        line = "\t\t{}{}= {}\t{}".format(self.prop, "\t" * (10 - (len(self.prop) // 4)),
                                         ",".join(self.value), self.comment)
        return line

    def is_changed(self):
        if self.value != self.default:
            return True


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

    def __repr__(self):
        # lines = []
        # for line_entry in self.properties:
        # 	lines.append(self.properties[line_entry].__repr__())
        #
        # response = "{}\n{}".format(self.name, "\n".join(lines))
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

    def has_property(self, prop):
        return prop in self.properties

    def is_artifact(self):
        for entry in self.properties:
            if self.properties[entry].name == "af_base":
                return True
        return False

    def is_armor(self):
        for entry in self.properties:
            if self.properties[entry].name == "outfit_actions":
                return True
        return False

    def is_weapon(self):
        for entry in self.properties:
            if self.properties[entry].name == "outfit_actions":
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
        if self.is_weapon():
            return "weapon"
        if self.is_ammo():
            return "ammo"
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
            if prop.value != prop.default or prop.lineno < 0:
                return True
        return False

    def todict(self):
        return {self.name: self}


class CraftingEntry(Entry):

    def __init__(self):
        Entry.__init__(self)
        self.quantity = 0
        self.fixed_quantity = False

    def set_entry(self, entry):
        self.load_from_entry(entry)
        self.quantity = 1
        self.name = entry.name

    def add(self, value=1):
        if self.fixed_quantity:
            return
        self.quantity += value

    def remove(self, value=1):
        if self.fixed_quantity:
            return
        self.quantity -= value
        if self.quantity < 0:
            self.quantity = 0