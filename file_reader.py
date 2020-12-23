from description_reader import translated_names
import os
import re
header_pattern = re.compile("^\[.*\]")
value_comparison_pattern = re.compile("(?<!{)=")


def split_all(filepath):
	allparts = []
	while 1:
		parts = os.path.split(filepath)
		if parts[0] == filepath:  # sentinel for absolute paths
			allparts.insert(0, parts[0])
			break
		elif parts[1] == filepath: # sentinel for relative paths
			allparts.insert(0, parts[1])
			break
		else:
			filepath = parts[0]
			allparts.insert(0, parts[1])
	return allparts


def remove_dirpath(path, dirpath):
	path = split_all(path)
	dirpath = split_all(dirpath)
	for index, n in enumerate(dirpath):
		if n == path[0]:
			path.pop(0)
	return os.path.join(*path)


# class Reader:
#     def __init__(self):
#         self.dirpath = ""
#         self.definitions = {}
#         self.files = {}
#         self.entries = {}
#         self.item_types = {}
#         self.item_groups = {}
#         self.inheritances = {}
#         self.object_lists = {}

# def set_dirpath(path):
# 	self.dirpath = os.path.join(*split_all(path))

def get_item_types(dirpath):
	item_groups = {}
	item_types = {}
	# pattern = re.compile("^\[.*\]")
	path = os.path.join(dirpath, "configs", "items", "trade", "presets", "trade_presets.ltx")
	if not os.path.exists(path):
		print("Wrong folder!")
		return
	with open(path, "r", encoding="ISO-8859-1") as infile:
		name = None
		for line in infile:
			if not line.strip():
				continue
			if line.startswith(";"):
				continue
			if "=" in line:
				continue
			match = re.match(header_pattern, line)
			if match is not None:
				name = match.group(0).replace("[", "").replace("]", "")
				if ":" in line:
					_, members = line.split(":")
					item_groups[name] = members.split(";")[0].strip().split(",")
					continue
				item_types[name] = []
				continue
			item_types[name].append(line.strip())
	return item_groups, item_types


def read_file(path, dirpath):
	entries = {}
	with open(path, "r", encoding="ISO-8859-1") as infile:
		file_entry = FileEntry(remove_dirpath(path, dirpath))
		entry = None
		counter = 0
		lineno = 0
		for line in infile:
			lineno += 1
			line = line.strip()
			match = re.match(header_pattern, line)
			if match is not None:
				# Place old entry into the file entry
				if entry is not None:
					file_entry.entries_order[counter] = entry
					entries[entry.name] = entry
					counter += 1
				###
				name = match.group(0).replace("[", "").replace("]", "")
				# Get parents
				parents = None
				if ":" in line:
					parents = line.split(":")[1]
					if ";" in parents:
						parents = parents.split(";")[0].strip()
					parents = [a.strip() for a in parents.split(",")]
				###

				entry = Entry()
				entry.load_data(name, parents, path, lineno)
				entry_line_no = 0
				continue
			if entry is None:
				file_entry.header.append(line)
				continue
			# Get comments for entry
			if line.strip().startswith(";") or not line.strip() or line.strip().startswith("--"):
				entry.comment_lines[entry_line_no] = line
				entry_line_no += 1
				continue
			comments = ""
			prop = line.strip()
			if ";" in prop:
				prop = prop.split(";")[0].strip()
				comments = ";".join(prop.split(";")[1:])
			###
			#  Get property
			match = re.search(value_comparison_pattern, prop)
			parent = None
			values = ""
			if match is not None:
				var = match.group(0)
				prop_name = prop.split(var)[0].strip()
				if len(prop.strip().split(var)) > 1:
					values = prop.strip().split(var)[1].strip()
			else:
				prop_name = prop
				parent = name
			if "," in values:
				values = [a.strip() for a in values.split(",")]
			else:
				values = [values]
			###
			line_entry = LineEntry(remove_dirpath(path, dirpath), entry_line_no,
								   entry.name, prop_name, parent, values, comments)
			entry.properties[prop_name] = line_entry
			entry_line_no += 1
		if entry is not None:
			file_entry.entries_order[counter] = entry
			entries[entry.name] = entry
	return file_entry, entries


def read_all_files(dirpath):
	files = {}
	all_entries = {}
	for x, y, z in os.walk(os.path.join(dirpath, "configs",  "items")):
		for f in z:
			path = os.path.join(x, f)
			file_entry, entries = read_file(path, dirpath)
			files[remove_dirpath(path, dirpath)] = file_entry
			for entry_name, entry in entries.items():
				all_entries[entry_name] = entry
	return files, all_entries


def read_items(dirpath):
	path = os.path.join(dirpath, "configs",  "defines.ltx")
	if not os.path.exists(path):
		print("Wrong folder!")
		return None, None
	file_entry, entries = read_file(path, dirpath)
	return file_entry, entries


def read_available_items(dirpath):
	item_types = {}
	item_groups = {}
	path = os.path.join(dirpath, "configs",  "items", "trade", "presets", "trade_presets.ltx")
	with open(path, "r", encoding="ISO-8859-1") as infile:
		name = None
		for line in infile:
			if not line.strip():
				continue
			if line.startswith(";"):
				continue
			if "=" in line:
				continue
			match = re.match(header_pattern, line)
			if match is None and name is not None:
				item_types[name].append(line.strip())
				continue
			name = match.group(0).replace("[", "").replace("]", "")
			if ":" in line:
				_, members = line.split(":")
				item_groups[name] = members.split(";")[0].strip().split(",")
				continue
			item_types[name] = []


def get_grouped_name_dict(item_types):
	output_dict = {}
	for key in item_types:
		output_dict[key] = []
		for tag in item_types[key]:
			if tag not in translated_names:
				continue
			name = translated_names[tag]
			output_dict[key].append((name, tag))
	return output_dict


def write_all(files, dirpath):
	for filename, entry in files.items():
		if not entry.is_changed():
			continue
		entry.write_file_entry(dirpath)


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
	def __init__(self, file, lineno, name, prop, parent, value, comment):
		self.file = file.strip()
		self.lineno = lineno
		self.name = name.strip()
		self.prop = prop.strip()
		self.parent = parent
		self.value = value
		self.default = value
		self.comment = comment.strip()
		self.level = 0

	def __repr__(self):
		return "{}: {}".format(self.prop, ",".join(self.value))

	def tolist(self):
		return [self.file, self.lineno, self.name, self.prop, self.parent, self.value, self.comment]

	def copy(self):
		new_entry = LineEntry(str(self.file), int(self.lineno), str(self.name), str(self.prop),
							  str(self.parent), list(self.value), str(self.comment))
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
		lines = []
		for line_entry in self.properties:
			lines.append(self.properties[line_entry].__repr__())

		response = "{}\n{}".format(self.name, "\n".join(lines))
		return response

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

		return "\n".join(output)

	def is_changed(self):
		for name, prop in self.properties.items():
			if prop.value != prop.default:
				return True
		return False


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


# if __name__ == "__main__":
    # reader = Reader()
    # reader.read_available_items()
    # print(reader.item_types)