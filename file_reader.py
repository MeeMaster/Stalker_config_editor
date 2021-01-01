from description_reader import translated_names
import os
import re

from entry_classes import FileEntry, LineEntry, Entry

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
								   entry.name, prop_name, values, comments)
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

# if __name__ == "__main__":
    # reader = Reader()
    # reader.read_available_items()
    # print(reader.item_types)