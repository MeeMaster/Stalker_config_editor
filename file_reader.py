from description_reader import translated_names
import os
import re

from entry_classes import FileEntry, LineEntry, Entry

header_pattern = re.compile("^\[.*\]")
value_comparison_pattern = re.compile("(?<!{)=")
condition_pattern = re.compile("{.*}")


def read_condition_from_value(value):
    match = re.match(condition_pattern, value)
    cond = ""
    if match is not None:
        cond = match.group(0)
    return cond


def split_all(filepath):
    allparts = []
    while 1:
        parts = os.path.split(filepath)
        if parts[0] == filepath:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == filepath:  # sentinel for relative paths
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
    path = None
    for x, y, z in os.walk(dirpath):
        for f in z:
            if "trade_presets.ltx" in f:
                path = os.path.join(x, f)
    if path is None:
        return None, None

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
    # entries = {}
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
                    # entries[entry.name] = entry
                    counter += 1
                ###
                name = match.group(0).replace("[", "").replace("]", "")
                # Get parents
                parents = []
                if ":" in line:
                    parents = line.split(":")[1]
                    if ";" in parents:
                        parents = parents.split(";")[0].strip()
                    parents = [a.strip() for a in parents.split(",")]
                ###

                entry = Entry()
                entry.load_data(name, parents, remove_dirpath(path, dirpath), lineno)
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
            equal = True
            if match is not None:
                var = match.group(0)
                prop_name = prop.split(var)[0].strip()
                if len(prop.strip().split(var)) > 1:
                    values = ",".join([a.strip() for a in var.join(prop.strip().split(var)[1:]).split(",")])
            else:
                prop_name = prop
                equal = False
                parent = name
            if "," in values:
                values = [a.strip() for a in values.split(",")]
            else:
                values = [values]
            ###
            conditions = []
            new_values = []
            for value in values:
                condition = read_condition_from_value(value)
                value = value.replace(condition, "").strip()
                new_values.append(value)
                conditions.append(condition)
            line_entry = LineEntry(remove_dirpath(path, dirpath), entry_line_no,
                                   entry.name, prop_name, new_values, conditions, comments)
            line_entry.equal_sign = equal
            entry.properties[prop_name] = line_entry
            entry_line_no += 1
        if entry is not None:
            file_entry.entries_order[counter] = entry
    return file_entry


def read_all_files(dirpath):
    files = {}
    for x, y, z in os.walk(os.path.join(dirpath, )):
        if "configs" not in x:
            continue
        if "scripts" in x or "plugins" in x or "\mp\\" in x or "\models\\" in x:
            continue
        for f in z:
            if ("craft" not in f and "parts" not in f) and "settings" in x:
                continue
            if os.path.splitext(f)[1] != ".ltx":
                continue
            path = os.path.join(x, f)
            file_entry = read_file(path, dirpath)
            files[remove_dirpath(path, dirpath)] = file_entry
    return files


def get_entries_from_file(file_entry):
    entries = {}
    for index, entry in file_entry.entries_order.items():
        entries[entry.name] = entry
    return entries


def get_grouped_name_dict(item_types):
    output_dict = {}
    for key in item_types:
        output_dict[key] = []
        for tag in item_types[key]:
            if tag in translated_names:
                name = translated_names[tag]
            else:
                name = tag
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