# Автомобиль ↔ Гараж

Исходный код находится в `src/`, тесты — в `tests/`, фотографии — в `Photos/`.
Путь к фотографиям вычисляется относительно исходного файла и не зависит от рабочего каталога.

Команды PowerShell из корня проекта (Python 3.14+, PyQt6):

```powershell
.\.venv\Scripts\python.exe src\car_garage.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Тесты используют стандартный `unittest`; проверки Qt выполняются без показа окон.
В PyCharm точка входа — `src/car_garage.py`.
