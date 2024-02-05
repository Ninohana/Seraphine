from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from app.components.champion_icon_widget import RoundIcon


class ChartIconLabel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.buffer = []

    def updateIcon(self, info):
        """

        @param info: dict[召唤师名: 英雄图标path]
        @return:
        """

        if self.buffer:
            for i, (name, championIcon) in enumerate(info.items()):
                self.buffer[i].image = QPixmap(championIcon)
            return

        for i, (name, championIcon) in enumerate(info.items()):
            icon = RoundIcon(championIcon, 28, 0, 2)
            self.vBoxLayout.addWidget(icon)
            self.buffer.append(icon)

            if i == 4:
                icon = QLabel()
                icon.setFixedSize(28, 28)
                self.vBoxLayout.addWidget(icon)

        self.vBoxLayout.setContentsMargins(
            18, self.height() * 0.168, 0, self.height() * 0.14)
