from PyQt5.QtWidgets import (QWidget, QSpacerItem, QVBoxLayout, QHBoxLayout, QLabel,  QSizePolicy)
from PyQt5.QtCore import QRect, Qt, QPoint
from PyQt5.QtGui import QPainter, QBrush, QColor
from images import load_icon_from_entry, load_hud_icon
from constants import *
from description_reader import translated_names


colors = {"green": QColor("darkGreen"), "light_green": QColor("green"), "red": QColor("darkRed"),
          "light_red": QColor("red"), "gray": QColor("gray")}


class ItemStatsDisplay(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.setFixedWidth(300)
        self.main_layout = QVBoxLayout()
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.name = QLabel()
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setStyleSheet("font: bold 16px;")
        self.stats = StatusBars()
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(self.name)
        self.main_layout.addWidget(self.stats)
        self.main_layout.addSpacerItem(QSpacerItem(2, 3, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(self.main_layout)

    def load_entry(self, entry):
        icon = load_icon_from_entry(entry)
        if icon is not None:
            self.icon.setPixmap(icon)
        if entry is None:
            return
        name = translated_names[entry.name] if entry.name in translated_names else entry.name
        self.name.setText(name)
        self.stats.load_data(entry)


class StatusBars(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

    def load_data(self, entry):
        self.clear_layout()
        if entry.is_armor():
            for name in armor_params_coeffs:
                if name not in entry.properties:
                    continue
                bar = StatusBar()
                bar.fill_values(entry.properties[name])
                self.main_layout.addWidget(bar)
        if entry.is_artifact():
            for name in artifact_params_coeffs:
                if name not in entry.properties:
                    continue
                bar = StatusBar()
                bar.fill_values(entry.properties[name])
                self.main_layout.addWidget(bar)

    def clear_layout(self):
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)


class StatusBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QHBoxLayout()
        self.icon = QLabel()
        self.icon.setFixedWidth(20)
        self.bar = Rectangle()
        self.bar.setFixedWidth(200)
        self.value = QLabel()
        self.value.setFixedWidth(50)
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(self.bar)
        self.main_layout.addWidget(self.value)
        self.setLayout(self.main_layout)

    def fill_values(self, line_entry):
        icon = load_hud_icon(line_entry.prop.replace("_immunity", "").replace("_protection", ""))
        value = float(line_entry.value[0])
        default = float(line_entry.default[0])
        coeff = 0
        max_val = 1000
        below_zero = False
        if line_entry.prop in armor_params_coeffs:
            coeff = armor_params_coeffs[line_entry.prop]
        elif line_entry.prop in artifact_params_coeffs:
            below_zero = True
            coeff = artifact_params_coeffs[line_entry.prop]
            max_val = maximal_values[artifact_units[line_entry.prop]]
        max_value = calculate_val_to_points(max_val, coeff)
        value = value / max_value
        default = default / max_value
        if icon is not None:
            self.icon.setPixmap(icon)
        self.bar.draw_rectangle(value, default, below_zero)


class Rectangle(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 180
        self.setGeometry(0, 0, self.width, 20)
        self.begin_bottom = QPoint()
        self.begin_top = QPoint()
        self.end_bottom = QPoint()
        self.end_top = QPoint()
        self.br1 = QBrush(QColor(100, 10, 10, 40))
        self.br2 = QBrush(QColor(100, 10, 10, 40))
        self.br3 = QBrush(QColor("darkGrey"))

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setBrush(self.br3)
        qp.drawRect(QRect(0, 0, self.width, 20))
        qp.setBrush(self.br1)
        qp.drawRect(QRect(self.begin_bottom, self.end_bottom))
        qp.setBrush(self.br2)
        qp.drawRect(QRect(self.begin_top, self.end_top))

    def draw_rectangle(self, value, default, below_zero):

        self.begin_bottom = QPoint(0, 0)
        self.begin_top = QPoint(0, 0)
        val1 = value * self.width
        val2 = default * self.width
        if below_zero:
            self.begin_bottom = QPoint(self.width/2, 0)
            self.begin_top = QPoint(self.width/2, 0)
            val1 = value * self.width/2 + self.width/2
            val2 = default * self.width/2 + self.width/2

        if val1 > val2:
            self.br1.setColor(colors["light_green"])
            self.br2.setColor(colors["green"])
            self.end_bottom = QPoint(val1, 20)
            self.end_top = QPoint(val2, 20)

        elif val1 < val2:
            self.br2.setColor(colors["light_red"])
            self.br1.setColor(colors["red"])
            self.end_bottom = QPoint(val2, 20)
            self.end_top = QPoint(val1, 20)

        else:
            self.br2.setColor(colors["gray"])
            self.br1.setColor(colors["gray"])
            self.end_bottom = QPoint(val1, 20)
            self.end_top = QPoint(val2, 20)
        self.update()

