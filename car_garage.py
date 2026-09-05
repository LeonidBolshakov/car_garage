from PyQt6.QtWidgets import QApplication
import sys

from main_window import MainWindow


def exception_hook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    traceback,
) -> None:
    sys.__excepthook__(exc_type, exc_value, traceback)

    app_hook = QApplication.instance()
    if app_hook is not None:
        app_hook.quit()


if __name__ == "__main__":
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
