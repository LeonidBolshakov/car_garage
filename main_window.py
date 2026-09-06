"""Главное окно приложения для случайного сопоставления автомобилей и гаражей."""

from pathlib import Path
import random

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

MS_DISPLAY_DELAY = 1500
SEC_START_RANDOM_TIME_INTERVAL = 7
SEC_STOP_RANDOM_TIME_INTERVAL = 15

INDICATOR_COLORS = (
    ("#4F6BED", "#3548A8"),
    ("#2F9E9A", "#1F6F6C"),
    ("#8E5BD9", "#613D99"),
)

INDICATOR_TEXT_COLOR = "white"


class MainWindow(QMainWindow):
    """Управляет интерфейсом и созданием случайных пар «автомобиль — гараж»."""

    def __init__(self) -> None:
        """Инициализирует главное окно, объекты и обработчики сигналов."""
        super().__init__()

        self._pair_number = 0  # Номер пары
        self._indicators: dict[tuple[int, int], QLabel] = {}  # тИндикаторы фотографий
        self.cars: list[int] = []
        self.garages: list[int] = []

        self._setting_main_window_view()
        self._setting_button_start()
        self._create_grid_for_photos_and_indicators()
        self._posting_photos_and_indicators()
        self._init_random_conformity()
        self._connects()
        self.leftover_pairs = min(len(self.cars), len(self.garages))

    def _setting_main_window_view(self):
        """Настраивает основные параметры главного окна и его layout."""
        self.setWindowTitle("Автомобиль <-> Гараж")
        self.resize(1200, 1200)

        # Центральный виджет окна
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Основной вертикальный layuot
        self.main_layout = QVBoxLayout(central_widget)

    def _setting_button_start(self):
        """Создаёт и размещает кнопку запуска случайного выбора пары."""
        self.button_start = QPushButton("Поехали!")

        font = QFont()
        font.setPointSize(20)
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
        """Создаёт сетку для фотографий автомобилей, гаражей и индикаторов."""
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setVerticalSpacing(4)

        self._grid.setColumnStretch(0, 1)  # левые фотографии
        self._grid.setColumnStretch(1, 0)  # левые индикаторы

        self._grid.setColumnMinimumWidth(2, 80)  # разделение сущностей
        self._grid.setColumnStretch(2, 0)

        self._grid.setColumnStretch(3, 0)  # правые индикаторы
        self._grid.setColumnStretch(4, 1)  # правые фотографии

        self.main_layout.addLayout(self._grid, 1)

    def _posting_photos_and_indicators(self):
        """Загружает фотографии и размещает их вместе с индикаторами в сетке."""
        l_row = 0
        r_row = 0
        for file in Path("./photos").iterdir():
            if not self._is_photo_file(file):
                continue

            photo = PhotoLabel(file)

            if file.name.startswith("L_"):
                self._add_and_style_widget_in_layuot(row=l_row, column=0, widget=photo)
                self._add_indicator(l_row, 1)
                self.cars.append(l_row)
                l_row += 1
            if file.name.startswith("R_"):
                self._add_indicator(r_row, 3)
                self._add_and_style_widget_in_layuot(row=r_row, column=4, widget=photo)
                self.garages.append(r_row)
                r_row += 1

        max_row = max(l_row, r_row)
        for row in range(max_row):
            self._grid.setRowStretch(row, 1)

    def _is_photo_file(self, file: Path) -> bool:
        """Проверяет, является ли путь поддерживаемым файлом изображения.

        Args:
            file: Путь к проверяемому файлу.

        Returns:
            True, если файл существует и имеет поддерживаемое расширение.
        """
        if not file.is_file():
            return False

        return file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}

    def _create_indicator(self, color: str | None = None) -> QLabel:
        """Создаёт индикатор заданного цвета.

        Args:
            color: Цвет фона индикатора. По умолчанию индикатор прозрачный.

        Returns:
            Созданный QLabel-индикатор.
        """
        if color is None:
            color = "transparent"

        indicator = QLabel()
        indicator.setFixedSize(24, 24)
        indicator.setStyleSheet(self._indicator_style_sheet(color))

        return indicator

    def _add_indicator(self, row: int, column: int) -> None:
        """Добавляет индикатор в указанную позицию сетки."""
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
        """Устанавливает цвет индикатора в указанной позиции.

        Args:
            row: Строка индикатора в сетке.
            column: Столбец индикатора в сетке.
            color: Цвет индикатора. По умолчанию прозрачный.
        """
        if color is None:
            color = "transparent"
        indicator = self._indicators[row, column]
        indicator.setStyleSheet(self._indicator_style_sheet(color))

    def set_random_indicator_color(
        self,
        row: int,
        column: int,
    ) -> None:
        """Устанавливает индикатору случайный цвет."""
        color = self.random_color()

        indicator = self._indicators[row, column]
        indicator.setStyleSheet(self._indicator_style_sheet(color))

    def _indicator_style_sheet(self, color: str) -> str:
        """Возвращает stylesheet обычного индикатора заданного цвета."""
        return f"""
            background-color: {color};
            border-radius: 12px;
        """

    def _busy_indicator_style_sheet(self):
        """Возвращает stylesheet индикатора объекта, включённого в пару."""
        # нумерация пар начинается с 1
        background, border = INDICATOR_COLORS[
            (self._pair_number - 1) % len(INDICATOR_COLORS)
        ]

        return f"""
            background-color: {background};
            color: {INDICATOR_TEXT_COLOR};
    
            border: {border};
            border-radius: 24px;
    
            font-size: 18px;
            font-weight: bold;
        """

    def _photo_widwet_style_sheet(self):
        """Возвращает stylesheet для рамки фотографии."""
        return "border: 1px solid lightgray;"

    def _connects(self):
        """Подключает сигналы элементов интерфейса к обработчикам."""
        self.button_start.clicked.connect(self.preparing_button_start)

    def _init_random_conformity(self):
        """Инициализирует модель случайного выбора автомобилей и гаражей."""
        self.random_conformity = RandomConformity()
        self.random_conformity.init_objects(self.cars, Type.CAR)
        self.random_conformity.init_objects(self.garages, Type.GARAGE)

    def wait_ms(self, ms: int) -> None:
        """Выполняет задержку, сохраняя обработку событий Qt.

        Args:
            ms: Длительность задержки в миллисекундах.
        """
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()

    def preparing_button_start(self):
        """Обрабатывает нажатие кнопки запуска и управляет её доступностью."""
        self.button_start.setEnabled(False)

        if self._create_random_car_garage_pair() and self.leftover_pairs > 0:
            self.button_start.setEnabled(True)

    def _create_random_car_garage_pair(self) -> bool:
        """Создаёт и отображает случайную пару «автомобиль — гараж».

        Returns:
            True, если пара успешно создана, иначе False.
        """
        self._pair_number += 1

        base_id = self.random_single_selection_with_animation()
        if base_id is None:
            return False

        self.set_and_show_object_is_occuped(
            row=base_id.object_id,
            column=self.get_indicator_column(base_id.object_type),
            object_id=base_id,
        )
        self.wait_ms(MS_DISPLAY_DELAY)

        opposite_type = Type.GARAGE if base_id.object_type == Type.CAR else Type.CAR
        opposite_id = self.random_single_selection_with_animation(filtr=opposite_type)
        if opposite_id is None:
            return False

        self.set_and_show_object_is_occuped(
            row=opposite_id.object_id,
            column=self.get_indicator_column(opposite_id.object_type),
            object_id=opposite_id,
        )

        self.leftover_pairs -= 1
        QApplication.beep()
        return True

    def set_and_show_object_is_occuped(
        self,
        row: int,
        column: int,
        object_id: Id,
    ) -> None:
        """Помечает объект занятым и отображает его принадлежность к паре.

        Args:
            row: Строка индикатора в сетке.
            column: Столбец индикатора в сетке.
            object_id: Идентификатор автомобиля или гаража.
        """

        self.random_conformity.set_object_is_occuped(object_id)
        self.set_appearance_of_busy_indicator(row=row, column=column)
        self.view_pair_number(row, column)

    def set_appearance_of_busy_indicator(self, row: int, column: int) -> None:
        """Оформляет индикатор как занятый объект найденной пары."""
        indicator = self._indicators[row, column]
        indicator.setFixedSize(48, 48)
        indicator.setStyleSheet(self._busy_indicator_style_sheet())
        indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def view_pair_number(self, row: int, column: int) -> None:
        """Отображает номер текущей пары на индикаторе."""
        item = self._grid.itemAtPosition(row, column)
        if item is None:
            return

        item.widget().setText(f"{self._pair_number}")

    def get_indicator_column(self, id_type: Type) -> int:
        """Возвращает столбец индикатора для автомобиля или гаража."""
        return 1 if id_type == Type.CAR else 3

    def random_single_selection_with_animation(
        self, filtr: Type | None = None
    ) -> Id | None:
        """Выполняет случайный выбор объекта с визуальной анимацией.

        Args:
            filtr: Тип выбираемого объекта. Если None, выбирается объект любого типа.

        Returns:
            Идентификатор последнего выбранного свободного объекта или None,
            если подходящих свободных объектов нет.
        """
        random_time_sec = random.randint(
            SEC_START_RANDOM_TIME_INTERVAL,
            SEC_STOP_RANDOM_TIME_INTERVAL,
        )  # случайное время в заданном интервале секунд
        number_random_iterations = int(
            random_time_sec * 1000 / MS_DISPLAY_DELAY
        )  # Количество итераций для реализации случайного времени

        result: Id | None = None
        for _ in range(number_random_iterations):
            result = self._find_and_show_single_random_object(filtr)
            if result is None:
                return None

        return result

    def _find_and_show_single_random_object(self, filtr: Type | None) -> Id | None:
        """Выбирает один свободный объект и кратковременно подсвечивает его.

        Args:
            filtr: Тип выбираемого объекта или None для выбора любого типа.

        Returns:
            Идентификатор выбранного объекта или None, если выбор невозможен.
        """

        selected_id = self.random_conformity.select_random_free_object(filtr=filtr)
        if selected_id is None:
            return None

        row = selected_id.object_id
        column = self.get_indicator_column(selected_id.object_type)

        self.set_random_indicator_color(
            row=row,
            column=column,
        )

        self.wait_ms(MS_DISPLAY_DELAY)

        self.set_indicator_color(
            row=row,
            column=column,
        )  # возвращаем цвет по умолчанию

        return selected_id

    def _add_and_style_widget_in_layuot(
        self, row: int, column: int, widget: QWidget
    ) -> None:
        """Применяет стиль к виджету и добавляет его в сетку."""
        widget.setStyleSheet(self._photo_widwet_style_sheet())
        self._grid.addWidget(widget, row, column)

    def random_color(self) -> str:
        """Возвращает случайный цвет в формате RGB для Qt stylesheet."""
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        return f"rgb({r}, {g}, {b})"
