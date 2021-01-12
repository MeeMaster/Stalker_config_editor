import os
import re
import xml.etree.ElementTree as ET

pattern = re.compile("\-{6,}")
start_pattern = "<!-{2}"
wrong_start_pattern = "<!-{3,}"
end_pattern = "-{2}>"
wrong_end_pattern = "-{3,}>"
xml_start_pattern = re.compile("<[^/^<^>]*>")
xml_end_pattern = re.compile("</[^>^<]*>")
whitespace = re.compile("^[\s]*")
# endspace = re.compile("[\s]*")

translated_names = {}
translated_descriptions = {}


def clean_line_and_check_comment_token(line: str):
    line = line.replace("&", "&#038;")
    match = re.search(start_pattern, line)
    opening = False
    if match is not None:
        match2 = re.search(wrong_start_pattern, line)
        opening = True
        if match2 is not None:
            line = line.replace(match2.group(0), "<!--")
            
    closing = False
    end_match = re.search(end_pattern, line)
    if end_match is not None:
        closing = True
        wrong_end_match = re.search(wrong_end_pattern, line)
        if wrong_end_match is not None:
            line = line.replace(wrong_end_match.group(0), "-->")
    return line, opening, closing


def fix_xml_file(infile, print_=False):
    text = infile.readlines()
    fixed_text = []
    last_line = ""
    is_open = False
    for index, line in enumerate(text):
        line = line.replace("\n", "")
        # if print_:
        #     print(line)
        line, opening, closing = clean_line_and_check_comment_token(line)
        # if print_:
        #     print(line)
        # line = clear_bad_formatting(line)
        if opening:
            if is_open:
                last_line = last_line.replace("\n", "-->\n")
            is_open = True
        if is_open:
            match = re.search(pattern, line)
            if match is not None:
                string = match.group(0)
                line = line.replace(string, string.replace("-", "_"))
        if closing:
            is_open = False
        fixed_text.append(last_line)
        last_line = line
    fixed_text.append(last_line)
    # print(fixed_text)
    for index, item in reversed(list(enumerate(fixed_text))):
        if not item:
            fixed_text.pop(index)
    return "\n".join(fixed_text)


def clear_bad_formatting(line):
    new_line = str(line)
    start_line = ""
    whites = ""
    w_spaces = re.search(whitespace, new_line)
    if w_spaces is not None:
        whites = w_spaces.group(0)
        new_line = new_line.replace(whites, "")
    match = re.findall(xml_start_pattern, new_line)
    for start_ in match:
        start_line += start_
        new_line = new_line.replace(start_, "")
    end_line = ""
    match = re.findall(xml_end_pattern, new_line)
    for end_ in match:
        end_line += end_
        new_line = new_line.replace(end_, "")
    if start_line or end_line:
        old_line = str(new_line)
        new_line = new_line.replace("<", "&lt;").replace(">", "&gt;")
    line = whites + start_line + new_line + end_line  # + "\n"
    return line


def get_file_paths(dirpath):
    eng = True
    filepaths = []
    # path = os.path.join(dirpath)
    for x, y, z in os.walk(dirpath):
        if os.path.join("text", "eng") not in x:
            continue
        for filename in z:
            if filename.startswith("_"):
                continue
            filepath = os.path.join(os.path.join(x, filename))
            filepaths.append(filepath)
    return filepaths


def read_descriptions(dirpath, entries):
    global translated_names
    global translated_descriptions
    names = {}
    descriptions = {}
    filepaths = get_file_paths(dirpath)
    for filepath in filepaths:
        new_names, new_descriptions = get_descriptions_from_file(filepath)
        names = {**names, **new_names}
        descriptions = {**descriptions, **new_descriptions}
    item_name_xml_dict = build_name_dict(entries)
    for item_name, item_xml_name in item_name_xml_dict.items():
        if item_xml_name[0] in names:
            translated_names[item_name] = names[item_xml_name[0]]
        # if item_xml_name[1] in descriptions:
        #     translated_descriptions[item_name] = descriptions[item_xml_name[1]]


def build_name_dict(entries):
    item_name_xml_dict = {}
    for name in entries:
        for prop_name, line_entry in entries[name].properties.items():
            if line_entry.prop != "inv_name":
                continue
            item_name_xml_dict[name] = line_entry.value
    return item_name_xml_dict


def get_descriptions_from_file(filepath):
    descriptions = {}
    names = {}
    with open(filepath, "r", encoding="ISO-8859-1") as infile:
        print_ = False
        if "st_quests_agroprom.xml" in filepath:
            print_ = True
        fixed_text = fix_xml_file(infile, print_)
    # with open("test", "w", encoding="ISO-8859-1") as outfile:
    #     outfile.write("".join(fixed_text))

    try:
        root = ET.fromstring(fixed_text)
    except ET.ParseError as e:
        # if e.code == 3:
        return names, descriptions
        # print(filepath)
        # continue
        # raise ET.ParseError(e)

    for child in root:
        _id = child.attrib["id"]
        for child2 in child:
            if "_descr" in _id:
                _id = _id.replace("_descr", "")
                descriptions[_id] = child2.text
                continue
            names[_id] = child2.text
    return names, descriptions


if __name__ == "__main__":
    read_descriptions()
    print(translated_names)