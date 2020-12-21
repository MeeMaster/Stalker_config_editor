from constants import parameter_icons
from PIL import Image
from io import BytesIO
from PyQt5.QtGui import QPixmap, QImage
from os import path
from file_reader import split_all

icons = None
status_icons = None


def load_equipment_icons(dirpath):
    global icons
    final_path = path.join(*split_all(dirpath), "textures", "ui", "ui_icon_equipment.dds")
    if not path.exists(final_path):
        if not path.exists(path.join("pics", "ui_icon_equipment.dds")):
            return
        final_path = path.join("pics", "ui_icon_equipment.dds")
    icons = Image.open(final_path)


def load_status_icons(dirpath):
    global status_icons
    final_path = path.join(*split_all(dirpath), "textures", "ui", "ui_hud.dds")
    if not path.exists(final_path):
        if not path.exists(path.join("pics", "ui_hud.dds")):
            return
        final_path = path.join("pics", "ui_hud.dds")
    status_icons = Image.open(final_path)


def load_all_icons(dirpath):
    load_equipment_icons(dirpath)
    load_status_icons(dirpath)


def get_icon_data(item_entry):
    start_x, start_y, size_x, size_y = None, None, None, None
    for name in item_entry.properties:
        if name == "inv_grid_x":
            start_x = int(item_entry.properties[name].value[0])
        if name == "inv_grid_y":
            start_y = int(item_entry.properties[name].value[0])
        if name == "inv_grid_width":
            size_x = int(item_entry.properties[name].value[0])
        if name == "inv_grid_height":
            size_y = int(item_entry.properties[name].value[0])
    return start_x, start_y, size_x, size_y


def load_icon_from_entry(entry):
    data = get_icon_data(entry)
    for a in data:
        if a is None:
            return None
    icon = load_icon(*data)
    return icon


def load_hud_icon(name):
    if status_icons is None:
        return None
    start_x, start_y = parameter_icons[name]
    grid_size = 18
    icon = status_icons.crop((start_x,
                              start_y,
                              (start_x+grid_size),
                              (start_y+grid_size))
                             )
    with BytesIO() as f:
        icon.save(f, format='png')
        f.seek(0)
        image_data = f.read()
        qimg = QImage.fromData(image_data)
        patch_qt = QPixmap.fromImage(qimg)
    return patch_qt


def load_icon(start_x, start_y, size_x, size_y):
    if icons is None:
        return None
    grid_size = 50
    icon = icons.crop((start_x * grid_size,
                       start_y * grid_size,
                       (start_x+size_x) * grid_size,
                       (start_y+size_y) * grid_size)
                      )
    with BytesIO() as f:
        icon.save(f, format='png')
        f.seek(0)
        image_data = f.read()
        qimg = QImage.fromData(image_data)
        patch_qt = QPixmap.fromImage(qimg)
    return patch_qt
