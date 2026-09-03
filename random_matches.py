from dataclasses import dataclass
from enum import auto, IntEnum
import random
from collections.abc import Sequence


class Type(IntEnum):
    CAR = auto()
    GARAGE = auto()


@dataclass(frozen=True, slots=True)
class Id:
    object_type: Type
    object_id: int


@dataclass
class CarOrGarage:
    correspondence: Id | None = None


type SequenceCarOrGarage = Sequence[CarOrGarage]


class RandomMatches:
    def __init__(self) -> None:
        self.objects: dict[Id, CarOrGarage] = {}
        self.is_init_cars_done: bool = False
        self.is_init_garage_done: bool = False

    def init_objects(self, objects_seguency: Sequence[int], object_type: Type) -> None:
        self._check_param_init_objects(objects_seguency, object_type)

        for object_num in objects_seguency:
            self.objects[
                Id(
                    object_type,
                    object_num,
                )
            ] = CarOrGarage(correspondence=None)

        if object_type == Type.CAR:
            self.is_init_cars_done = True

        if object_type == Type.GARAGE:
            self.is_init_garage_done = True

    def _check_param_init_objects(
        self, objects_seguency: Sequence[int], object_type: Type
    ) -> None:
        if not isinstance(objects_seguency, Sequence):
            raise TypeError(
                "Класс RandomMatches. Метод init_cars\n"
                "Первый параметр должен иметь тип Sequence"
            )

        if not isinstance(object_type, Type):
            raise TypeError(
                "Класс RandomMatches. Метод init_cars\n"
                "Второй параметр должен иметь тип Type"
            )

        if self.is_init_cars_done:
            raise RuntimeError(
                "Класс RandomMatches. Метод init_cars\n"
                "Объеты типа Type.CAR уже инициализированы"
            )
        if self.is_init_garage_done:
            raise RuntimeError(
                "Класс RandomMatches. Метод init_cars\n"
                "Объеты типа Type.GARAGE уже инициализированы"
            )

    def set_correspondences(self, object_a_id: Id, object_b_id: Id) -> None:
        self._check_param_set_correspondences(object_a_id, object_b_id)

        self.objects[object_a_id].correspondence = object_b_id
        self.objects[object_b_id].correspondence = object_a_id

    def _check_param_set_correspondences(
        self, object_a_id: Id, object_b_id: Id
    ) -> None:
        if not (isinstance(object_a_id, Id) and isinstance(object_b_id, Id)):
            raise TypeError(
                "Класс RandomMatches. Метод set_correspondences\n"
                "Параметры должны иметь тип Id"
            )

        if object_a_id.object_type == object_b_id.object_type:
            raise ValueError(
                "Класс RandomMatches. Метод set_correspondences\n"
                "Объекты параметоров должны иметь разные типы ('Авто' и 'Гараж')"
            )

    def _is_free_object(self, obect_id: Id) -> bool:
        self._check_param_is_busy(obect_id)

        return self.objects[obect_id].correspondence is None

    def _check_param_is_busy(self, obect_id: Id) -> None:
        if not isinstance(obect_id, Id):
            raise TypeError(
                "Класс RandomMatches. Метод is_busy_object\n"
                "Параметр должен иметь тип Id"
            )

    def selecting_random_free_object(self, filtr: Type | None) -> Id | None:
        self._check_param_selecting_random_free_object(filtr)

        free_objects: list = []
        for currrent_object_id in self.objects:
            if filtr is not None and currrent_object_id.object_type != filtr:
                continue

            if self._is_free_object(currrent_object_id):
                free_objects.append(currrent_object_id)

        if not free_objects:
            return None

        return random.choice(free_objects).id

    def _check_param_selecting_random_free_object(self, filtr: Type | None) -> None:
        if filtr is not None and not isinstance(filtr, Type):
            raise TypeError(
                "Класс RandomMatches. Метод selecting_random_free_object\n"
                "Параметр должен иметь тип Type или быть None"
            )
