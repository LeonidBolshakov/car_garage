"""Проверки загрузки ресурсов и создания пар без показа окна и задержек."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtWidgets import QApplication

from car_garage import exception_hook
from main_window import MainWindow, PHOTOS_DIR
from photolabel import PhotoLabel
from random_matches import Id, Type


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_window(self):
        window = MainWindow()
        self.addCleanup(window.close)
        return window

    def test_loads_project_photos_from_unrelated_working_directory(self):
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                window = self.make_window()
            finally:
                os.chdir(original)
        files = [file for file in PHOTOS_DIR.iterdir() if window._is_photo_file(file)]
        self.assertEqual(len(window.cars), sum(file.name.startswith("L_") for file in files))
        self.assertEqual(len(window.garages), sum(file.name.startswith("R_") for file in files))
        self.assertGreater(window.leftover_pairs, 0)
        labels = window.findChildren(PhotoLabel)
        self.assertTrue(labels)
        self.assertTrue(all(not label._original_pixmap.isNull() for label in labels))

    def test_pair_marks_both_objects_and_disables_button_after_last_pair(self):
        window = self.make_window()
        count = window.leftover_pairs
        choices = [item for index in range(count) for item in (Id(Type.CAR, index), Id(Type.GARAGE, index))]
        with patch.object(window, "random_single_selection_with_animation", side_effect=choices), patch.object(window, "wait_ms"), patch.object(QApplication, "beep"):
            for index in range(count):
                window._preparing_button_start()
                self.assertEqual(window.leftover_pairs, count - index - 1)
                for kind, column in ((Type.CAR, 1), (Type.GARAGE, 3)):
                    self.assertTrue(window.random_conformity.objects[Id(kind, index)].busy)
                    self.assertEqual(window._indicators[index, column].text(), str(index + 1))
                self.assertEqual(window.button_start.isEnabled(), index < count - 1)

    def test_photo_filter_checks_extension_and_file_existence(self):
        window = self.make_window()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, expected in (("photo.JPG", True), ("photo.png", True), ("photo.jpeg", True), ("photo.webp", True), ("notes.txt", False)):
                file = root / name
                file.touch()
                self.assertEqual(window._is_photo_file(file), expected)
            self.assertFalse(window._is_photo_file(root / "missing.jpg"))
            folder = root / "folder.jpg"
            folder.mkdir()
            self.assertFalse(window._is_photo_file(folder))

    def test_photo_resize_preserves_aspect_ratio(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "photo.png"
            pixmap = QPixmap(200, 100)
            pixmap.fill()
            self.assertTrue(pixmap.save(str(file)))
            label = PhotoLabel(file)
            self.addCleanup(label.close)
            label.resize(100, 100)
            label.resizeEvent(QResizeEvent(QSize(100, 100), QSize(200, 100)))
            self.assertEqual(label.pixmap().size(), QSize(100, 50))

    def test_exception_hook_reports_exception_and_quits(self):
        error = RuntimeError("test")
        with patch("sys.__excepthook__") as report, patch("car_garage.QApplication.instance") as instance:
            exception_hook(RuntimeError, error, None)
            report.assert_called_once_with(RuntimeError, error, None)
            instance.return_value.quit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
