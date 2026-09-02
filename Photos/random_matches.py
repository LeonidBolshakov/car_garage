from dataclasses import dataclass
from enum import auto, IntEnum
from typing import Sequence
import random


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
    def __init__(self):
        self.objects: dict[Id, CarOrGarage] = {}
        self.is_init_cars_done: bool = False
        self.is_init_garage_done: bool = False

    def init_objects(self, objects: SequenceCarOrGarage, object_type: Type):
        if not isinstance(objects, SequenceCarOrGarage):
            raise TypeError(
                "Класс RandomMatches. Метод init_cars\n"
                "Первый параметр должен иметь тип SequenceCarOrGarage"
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

        for object_num in range(objects):
            self.objects[
                Id(
                    object_num,
                    object_type,
                )
            ] = CarOrGarage(correspondence=None)

        if object_type == Type.CAR:
            self.is_init_cars_done = True

        if object_type == Type.GARAGE:
            self.is_init_garage_done = True

    def set_correspondence(self, object_id: Id, correspondence: Id):
        if not isinstance(object_id, Id):
            raise TypeError(
                "Класс RandomMatches. Метод set_status_busy\n"
                "Первый параметр должен иметь тип Id"
            )
        self.objects[object_id].correspondence = correspondence

        self.objects[
            Id(
                not object_id.object_type,
                correspondence,
            )
        ].correspondence = object_id

    def is_busy(self, obect_id: Id) -> Status:
        if not isinstance(obect_id, Id):
            raise TypeError(
                "Класс RandomMatches. Метод get_status_busy\n"
                "Первый параметр должен иметь тип Id"
            )

        return self.objects[obect_id].correspondence

    def selecting_random_free_object(
        self, filtr: selecting_random_free_object | None
    ) -> CarOrGarage | None:
        if not isinstance(filtr, (Type, None)):
            raise TypeError(
                "Класс RandomMatches. Метод selecting_random_free_object\n"
                "Первый параметр должен иметь тип Type или None"
            )

        free_objects: list = []
        for currrent_object in self.objects:
            if filtr is not None and currrent_object.object_id.object_type != filtr:
                continue

            if self.is_busy(currrent_object.object_id):
                free_objects.append(currrent_object)

        if not free_objects:
            return None

        return random.choice(free_objects)
