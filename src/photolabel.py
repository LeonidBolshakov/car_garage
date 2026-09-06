"""Виджет для отображения фотографии с сохранением пропорций."""

from pathlib import Path

from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt


class PhotoLabel(QLabel):
    """QLabel, автоматически масштабирующий фотографию под размер виджета."""

    def __init__(self, file: Path) -> None:
        """Загружает исходное изображение и настраивает виджет.

        Args:
            file: Путь к файлу изображения.
        """
        super().__init__()

        self._original_pixmap = QPixmap(str(file))

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        """Масштабирует изображение при изменении размера виджета, сохраняя пропорции."""
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
