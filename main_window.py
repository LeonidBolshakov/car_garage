from pathlib import Path
import random
from typing import NamedTuple

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QApplication,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, QEventLoop

from random_matches import RandomConformity, Type, Id
from photolabel import PhotoLabel

MS_FLICKER_DELAY = 1500
SEC_START_RANDOM_TIME_INTERVAL = 5
SEC_STOP_RANDOM_TIME_INTERVAL = 10


class IdColor(NamedTuple):
    Id: Id
    color: str


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._indicators: dict[tuple[int, int], QLabel] = {}
        self.cars: list[int] = []
        self.garages: list[int] = []

        self._setting_window_view()
        self._setting_button_start()
        self._create_grid_for_photos_and_indicators()
        self._posting_photos_and_indicators()
        self._init_random_conformity()
        self._connects()

    def _setting_window_view(self):
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
            if not self._is_photo_file(file):
                continue

            photo = PhotoLabel(file)

            if file.name.startswith("L_"):
                self._grid.addWidget(photo, l_row, 0)
                self._add_indicator(l_row, 1)
                self.cars.append(l_row)
                l_row += 1
            if file.name.startswith("R_"):
                self._add_indicator(r_row, 3)
                self._grid.addWidget(photo, r_row, 4)
                self.garages.append(r_row)
                r_row += 1

        row_count = max(l_row, r_row)
        for row in range(row_count):
            self._grid.setRowStretch(row, 1)

    def _is_photo_file(self, file: Path) -> bool:
        if not file.is_file():
            return False

        if not file.suffix.lower() in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            return False

        return True

    def _create_indicator(self, color: str | None = None) -> QLabel:
        if color is None:
            color = "transparent"

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

    def set_random_indicator_color(
        self,
        row: int,
        column: int,
    ) -> str:
        color = self.random_conformity.random_color()

        indicator = self._indicators[row, column]
        indicator.setStyleSheet(self._indicator_style_sheet(color))

        return color

    def _indicator_style_sheet(self, color: str) -> str:
        return f"""
            background-color: {color};
            border-radius: 12px;
        """

    def _connects(self):
        self.button_start.clicked.connect(self.preparing_button_start)

    def _init_random_conformity(self):
        self.random_conformity = RandomConformity()
        self.random_conformity.init_objects(self.cars, Type.CAR)
        self.random_conformity.init_objects(self.garages, Type.GARAGE)

    def wait_ms(self, ms: int) -> None:
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()

    def preparing_button_start(self):
        self.button_start.setEnabled(False)

        if self._find_cars_and_garages():
            self.button_start.setEnabled(True)

    def _find_cars_and_garages(self) -> bool:

        id_color = self.random_selection_with_animation()
        if id_color is None:
            return False
        self.set_shape_of_indicator(
            row=id_color.Id.object_id,
            column=self.get_indicator_column(id_color.Id.object_type),
        )

        self.random_conformity.set_object_is_occuped(id_color.Id)
        self.set_indicator_color(
            row=id_color.Id.object_id,
            column=self.get_indicator_column(id_color.Id.object_type),
            color=id_color.color,
        )

        opposite_type = Type.GARAGE if id_color.Id.object_type == Type.CAR else Type.CAR
        opposite_id_color = self.random_selection_with_animation(filtr=opposite_type)
        if opposite_id_color is None:
            return False

        # self.set_and_show_object_is_occuped(r)

        self.random_conformity.set_object_is_occuped(opposite_id_color.Id)
        self.set_indicator_color(
            row=opposite_id_color.Id.object_id,
            column=self.get_indicator_column(opposite_id_color.Id.object_type),
            color=id_color.color,
        )

        self.set_shape_of_indicator(
            row=opposite_id_color.Id.object_id,
            column=self.get_indicator_column(opposite_id_color.Id.object_type),
        )
        QApplication.beep()
        return True

    def set_and_show_object_is_occuped(
        self,
        row: int,
        column: int,
        id_color: IdColor,
    ) -> None:
        self.random_conformity.set_object_is_occuped(id_color.Id)
        self.set_indicator_color(row=row, column=column, color=id_color.color)
        self.set_shape_of_indicator(row=row, column=column)

    def set_shape_of_indicator(self, row: int, column: int) -> None:
        indicator = self._indicators[row, column]
        indicator.setFixedSize(48, 48)

    def get_indicator_column(self, id_type: Type) -> int:
        return 1 if id_type == Type.CAR else 3

    def random_selection_with_animation(
        self, filtr: Type | None = None
    ) -> IdColor | None:

        random_time_sec = random.randint(
            SEC_START_RANDOM_TIME_INTERVAL,
            SEC_STOP_RANDOM_TIME_INTERVAL,
        )  # случайное время в заданном интервале секунд
        number_random_iterations = int(
            random_time_sec * 1000 / MS_FLICKER_DELAY
        )  # Количество итераций для реализации случайного времени

        result: IdColor | None = None
        for _ in range(number_random_iterations):
            result = self._flash_single_random_object(filtr)
            if result is None:
                return None

        return result

    def _flash_single_random_object(self, filtr: Type | None) -> IdColor | None:

        selected_id = self.random_conformity.selecting_random_free_object(filtr=filtr)
        if selected_id is None:
            return None

        row = selected_id.object_id
        column = self.get_indicator_column(selected_id.object_type)

        color = self.set_random_indicator_color(
            row=row,
            column=column,
        )

        self.wait_ms(MS_FLICKER_DELAY)

        self.set_indicator_color(
            row=row,
            column=column,
        )

        return IdColor(selected_id, color)
