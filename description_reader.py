import os
import re
import xml.etree.ElementTree as ET

pattern = re.compile("\-{6,}")
start_pattern = "<!-{2}"
wrong_start_pattern = "<!-{3,}"
end_pattern = "-{2}>"
wrong_end_pattern = "-{3,}>"

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


def fix_xml_file(infile):
    text = infile.readlines()
    fixed_text = []
    last_line = ""
    is_open = False
    for line in text:
        line, opening, closing = clean_line_and_check_comment_token(line)
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
    return "".join(fixed_text)


def get_file_paths(dirpath):
    eng = True
    filepaths = []
    path = os.path.join(dirpath, "configs",  "text", "eng" if eng else "rus")
    for _, _, z in os.walk(path):
        for filename in z:
            if filename.startswith("_"):
                continue
            filepath = os.path.join(path, filename)
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
        fixed_text = fix_xml_file(infile)
    # with open("test", "w", encoding="ISO-8859-1") as outfile:
    #     outfile.write("".join(fixed_text))

    try:
        root = ET.fromstring(fixed_text)
    except ET.ParseError as e:
        if e.code == 3:
            return names, descriptions
        raise ET.ParseError(e)

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