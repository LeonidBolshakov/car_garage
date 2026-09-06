"""Модель хранения и случайного выбора автомобилей и гаражей."""

from dataclasses import dataclass
from enum import auto, IntEnum
import random
from collections.abc import Sequence


class Type(IntEnum):
    """Тип объекта, участвующего в создании пары."""
    CAR = auto()
    GARAGE = auto()


@dataclass(frozen=True, slots=True)
class Id:
    """Идентификатор автомобиля или гаража."""
    object_type: Type
    object_id: int


@dataclass
class CarOrGarage:
    """Хранит текущее состояние занятости автомобиля или гаража."""
    busy: bool = False


class RandomConformity:
    """Хранит объекты и предоставляет случайный выбор свободного объекта."""

    def __init__(self) -> None:
        """Создаёт пустое хранилище объектов и признаки их инициализации."""
        self.objects: dict[Id, CarOrGarage] = {}
        self.is_init_cars_done: bool = False
        self.is_init_garage_done: bool = False

    def init_objects(self, objects_ids: Sequence[int], object_type: Type) -> None:
        """Добавляет в хранилище объекты указанного типа.

        Args:
            objects_ids: Последовательность идентификаторов объектов.
            object_type: Тип добавляемых объектов.

        Raises:
            RuntimeError: Если объекты этого типа уже были инициализированы.
        """
        self._check_param_init_objects(objects_ids, object_type)

        for object_num in objects_ids:
            self.objects[
                Id(
                    object_type,
                    object_num,
                )
            ] = CarOrGarage()

        if object_type == Type.CAR:
            self.is_init_cars_done = True

        if object_type == Type.GARAGE:
            self.is_init_garage_done = True

    def _check_param_init_objects(
        self, objects_ids: Sequence[int], object_type: Type
    ) -> None:
        """Проверяет, не выполнялась ли ранее инициализация указанного типа.

        Args:
            objects_ids: Последовательность идентификаторов объектов.
            object_type: Тип инициализируемых объектов.

        Raises:
            RuntimeError: Если объекты указанного типа уже инициализированы.
        """
        if object_type == Type.CAR and self.is_init_cars_done:
            raise RuntimeError(
                "RandomConformity.init_objects(): "
                "объекты Type.CAR уже инициализированы"
            )

        if object_type == Type.GARAGE and self.is_init_garage_done:
            raise RuntimeError(
                "RandomConformity.init_objects(): "
                "объекты Type.GARAGE уже инициализированы"
            )

    def _is_free_object(self, object_id: Id) -> bool:
        """Проверяет, свободен ли объект.

        Args:
            object_id: Идентификатор проверяемого объекта.

        Returns:
            True, если объект свободен, иначе False.
        """

        return not self.objects[object_id].busy

    def select_random_free_object(self, filtr: Type | None = None) -> Id | None:
        """Выбирает случайный свободный объект.

        Args:
            filtr: Тип выбираемого объекта. Если None, учитываются оба типа.

        Returns:
            Идентификатор случайного свободного объекта или None, если таких нет.
        """

        free_objects: list[Id] = []
        for current_object_id in self.objects:
            if filtr is not None and current_object_id.object_type != filtr:
                continue

            if self._is_free_object(current_object_id):
                free_objects.append(current_object_id)

        if not free_objects:
            return None

        return random.choice(free_objects)

    def set_object_is_occuped(self, object_id: Id) -> None:
        """Помечает объект как занятый.

        Args:
            object_id: Идентификатор объекта.
        """
        self.objects[object_id].busy = True
