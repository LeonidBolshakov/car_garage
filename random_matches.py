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
    busy: bool = False


type SequenceCarOrGarage = Sequence[CarOrGarage]


class RandomConformity:
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
            ] = CarOrGarage()

        if object_type == Type.CAR:
            self.is_init_cars_done = True

        if object_type == Type.GARAGE:
            self.is_init_garage_done = True

    def _check_param_init_objects(
        self, objects_seguency: Sequence[int], object_type: Type
    ) -> None:
        if object_type == Type.CAR and self.is_init_cars_done:
            raise RuntimeError(
                "Класс RandomConformity. Метод init_cars\n"
                "Объеты типа Type.CAR уже инициализированы"
            )

        if object_type == Type.GARAGE and self.is_init_garage_done:
            raise RuntimeError(
                "Класс RandomConformity. Метод init_cars\n"
                "Объеты типа Type.GARAGE уже инициализированы"
            )

    def _is_free_object(self, obect_id: Id) -> bool:

        return not self.objects[obect_id].busy

    def selecting_random_free_object(self, filtr: Type | None = None) -> Id | None:

        free_objects: list = []
        for currrent_object_id in self.objects:
            if filtr is not None and currrent_object_id.object_type != filtr:
                continue

            if self._is_free_object(currrent_object_id):
                free_objects.append(currrent_object_id)

        if not free_objects:
            return None

        return random.choice(free_objects)

    def random_color(self) -> str:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        return f"rgb({r}, {g}, {b})"

    def set_object_is_occuped(self, object_id: Id) -> None:
        self.objects[object_id].busy = True
