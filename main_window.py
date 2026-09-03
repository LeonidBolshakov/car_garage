from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QGridLayout,
    QSizePolicy,
    QLabel,
)
from PyQt6.QtGui import QFont, QPixmap, QResizeEvent
from PyQt6.QtCore import Qt, QTimer

MS_FLICKER_DELAY = 1000


class PhotoLabel(QLabel):
    def __init__(self, file: Path) -> None:
        super().__init__()

        self._original_pixmap = QPixmap(str(file))

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        super().resizeEvent(a0)

        if self._original_pixmap.isNull():
            return

        target_size = self.contentsRect().size()

        if target_size.isEmpty():
            return

        scaled_pixmap = self._original_pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled_pixmap)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._indicators: dict[tuple[int, int], QLabel] = {}
        self._setting_window_appearance()
        self._setting_button_start()
        self._create_grid_for_photos_and_indicators()
        self._posting_photos_and_indicators()
        self._connects()

    def _setting_window_appearance(self):
        self.setWindowTitle("Автомобиль <-> Гараж")
        self.resize(1200, 1200)

        # Центральный виджет окна
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Основной вертикальный layuot
        self.main_layout = QVBoxLayout(central_widget)

    def _setting_button_start(self):
        self.button_start = QPushButton("Поехали!")

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.button_start.setFont(font)

        self.button_start.setStyleSheet("color: red")
        self.button_start.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        self.main_layout.addWidget(
            self.button_start,
            alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
        )

    def _create_grid_for_photos_and_indicators(self):
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(5)
        self._grid.setVerticalSpacing(4)

        self._grid.setColumnStretch(0, 1)  # левые фотографии
        self._grid.setColumnStretch(1, 0)  # левые индикаторы

        self._grid.setColumnMinimumWidth(2, 80)  # разделение сущностей
        self._grid.setColumnStretch(2, 0)

        self._grid.setColumnStretch(3, 0)  # правые индикаторы
        self._grid.setColumnStretch(4, 1)  # правые фотографии

        self.main_layout.addLayout(self._grid, 1)

    def _posting_photos_and_indicators(self):
        l_row = 0
        r_row = 0
        for file in Path("./photos").iterdir():
            if not file.is_file():
                continue
            if not file.suffix.lower() in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
            }:
                continue

            photo = PhotoLabel(file)

            if file.name.startswith("L_"):
                self._grid.addWidget(photo, l_row, 0)
                self._add_indicator(l_row, 1)
                if l_row == 2:
                    self.set_indicator_blick(l_row, 1)
                l_row += 1
            if file.name.startswith("R_"):
                self._add_indicator(r_row, 3)
                self._grid.addWidget(photo, r_row, 4)
                r_row += 1

        row_count = max(l_row, r_row)
        for row in range(row_count):
            self._grid.setRowStretch(row, 1)

    def _create_indicator(self, color: str = "gray") -> QLabel:
        indicator = QLabel()
        indicator.setFixedSize(24, 24)
        indicator.setStyleSheet(self._indicator_style_sheet(color))

        return indicator

    def _add_indicator(self, row: int, column: int) -> None:
        indicator = self._create_indicator()
        self._grid.addWidget(
            indicator,
            row,
            column,
            Qt.AlignmentFlag.AlignCenter,
        )
        self._indicators[(row, column)] = indicator

    def set_indicator_color(
        self,
        row: int,
        column: int,
        color: str | None = None,
    ) -> None:
        if color is None:
            color = "transparent"
        indicator = self._indicators[row, column]
        indicator.setStyleSheet(self._indicator_style_sheet(color))

    def set_indicator_blick(
        self,
        row: int,
        column: int,
        color: str | None = None,
    ) -> None:
        if color is None:
            color = "yellow"
        indicator = self._indicators[row, column]
        indicator.setStyleSheet(self._indicator_style_sheet(color))
        QTimer.singleShot(
            MS_FLICKER_DELAY,
            lambda: self.set_indicator_color(row, column),
        )

    def _indicator_style_sheet(self, color: str | None = None) -> str:
        return f"""
            background-color: {color};
            border-radius: 12px;
        """

    def _connects(self):
        self.button_start.clicked.connect(self.preparing_button_start)

    def preparing_button_start(self):
        pass
