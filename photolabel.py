from pathlib import Path

from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt


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
