from constants import parameter_icons
# from PIL import Image
# from io import BytesIO
from PyQt5.QtGui import QPixmap#, QImage
from os import path
from file_reader import split_all

icons = None
status_icons = None


def load_equipment_icons():
    global icons
    final_path = path.join("pics", "ui_icon_equipment.png")
    icons = QPixmap(final_path)


def load_status_icons():
    global status_icons
    final_path = path.join("pics", "ui_hud.png")
    status_icons = QPixmap(final_path)


def load_all_icons():
    load_equipment_icons()
    load_status_icons()


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
    copy = status_icons.copy(start_x, start_y, grid_size, grid_size)
    return copy


def load_icon(start_x, start_y, size_x, size_y):
    if icons is None:
        return None
    grid_size = 50
    copy = icons.copy(start_x * grid_size,
                      start_y * grid_size,
                      size_x * grid_size,
                      size_y * grid_size)
    return copy
