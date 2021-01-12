from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLineEdit

from description_reader import translated_names
from images import load_icon_from_entry #, #all_item_icons


class ItemRepresentation(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, entry):
        QWidget.__init__(self)
        self.entry = entry
        self.main_layout = QVBoxLayout()
        self.image = QLabel()
        self.image.setFixedWidth(100)
        self.image.setFixedHeight(100)
        self.image.setAlignment(Qt.AlignCenter)
        self.label = QLabel()
        self.label.setMaximumWidth(70)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.main_layout.addWidget(self.image)
        self.main_layout.addWidget(self.label)
        self.load_data(entry)
        # self.connect(self.emit_change)
        self.setLayout(self.main_layout)

    def load_data(self, entry):

        translated_name = translated_names[entry.name] if entry.name in translated_names else entry.name
        self.label.setText(translated_name)
        # icon = None
        # if entry.name in all_item_icons:
        # icon = all_item_icons[entry.name]
        icon = load_icon_from_entry(entry)
        if icon is None:
            return
        self.image.setPixmap(icon)

    def mouseDoubleClickEvent(self, event):
        self.clicked.emit(self.entry.name)


class CraftingItemRepresentation(ItemRepresentation):
    value_changed = pyqtSignal(str, int)

    def __init__(self, entry):
        ItemRepresentation.__init__(self, entry)
        self.counter_layout = QHBoxLayout()
        self.main_layout.addLayout(self.counter_layout)
        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(15)
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(15)
        self.value_view = QLabel()
        self.value_view.setAlignment(Qt.AlignCenter)
        self.value_view.setFixedWidth(15)
        self.counter_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.counter_layout.addWidget(self.minus_button)
        self.counter_layout.addWidget(self.value_view)
        self.counter_layout.addWidget(self.plus_button)
        self.counter_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.minus_button.clicked.connect(lambda: self.change_value(False))
        self.plus_button.clicked.connect(lambda: self.change_value(True))
        self.single = False
        self.update_view()

    def change_value(self, add=True):
        if self.single:
            return
        if add:
            self.entry.add()
        else:
            self.entry.remove()
        self.update_view()
        self.value_changed.emit(self.entry.name, self.entry.quantity)

    def set_single_item(self, setting):
        self.single = setting
        self.minus_button.setEnabled(not setting)
        self.plus_button.setEnabled(not setting)

    def update_view(self):
        self.value_view.setText(str(self.entry.quantity))


class TradeItemRepresentation(CraftingItemRepresentation):
    chance_changed = pyqtSignal(str, float)

    def __init__(self, entry):
        CraftingItemRepresentation.__init__(self, entry)
        self.restock_label = QLabel("Restock chance")
        self.restock_value = QLineEdit()
        self.restock_value.setValidator(QDoubleValidator(0., 1., 2))
        self.restock_value.setText(str(entry.chance))
        self.restock_value.setMaximumWidth(50)
        self.restock_value.setAlignment(Qt.AlignCenter)
        self.restock_value.editingFinished.connect(self.change_chance)
        self.main_layout.addWidget(self.restock_label)
        self.main_layout.addWidget(self.restock_value)

    def change_chance(self):
        self.chance_changed.emit(self.entry.name, float(self.restock_value.text().replace(",", ".")))

