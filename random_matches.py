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


class RandomConformity:
    def __init__(self) -> None:
        self.objects: dict[Id, CarOrGarage] = {}
        self.is_init_cars_done: bool = False
        self.is_init_garage_done: bool = False

    def init_objects(self, objects_ids: Sequence[int], object_type: Type) -> None:
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

        return not self.objects[object_id].busy

    def select_random_free_object(self, filtr: Type | None = None) -> Id | None:

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
        self.objects[object_id].busy = True
