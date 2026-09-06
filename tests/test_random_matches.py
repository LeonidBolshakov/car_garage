"""Проверки выбора свободных объектов без зависимости от случайного результата."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from random_matches import Id, RandomConformity, Type


class RandomConformityTests(unittest.TestCase):
    def setUp(self):
        self.model = RandomConformity()

    def test_empty_storage_returns_none(self):
        for kind in (None, Type.CAR, Type.GARAGE):
            with self.subTest(kind=kind):
                self.assertIsNone(self.model.select_random_free_object(kind))

    def test_same_number_can_identify_car_and_garage(self):
        for kind in Type:
            self.model.init_objects([0], kind)
        self.assertEqual(set(self.model.objects), {Id(Type.CAR, 0), Id(Type.GARAGE, 0)})
        self.assertTrue(all(not obj.busy for obj in self.model.objects.values()))

    def test_reinitialization_rejected_without_changing_objects(self):
        for kind in Type:
            with self.subTest(kind=kind):
                model = RandomConformity()
                model.init_objects([0], kind)
                with self.assertRaises(RuntimeError):
                    model.init_objects([1], kind)
                self.assertEqual(set(model.objects), {Id(kind, 0)})

    def test_filter_and_occupied_objects(self):
        self.model.init_objects([0, 1], Type.CAR)
        self.model.init_objects([0], Type.GARAGE)
        self.model.set_object_is_occuped(Id(Type.CAR, 0))
        self.assertEqual(self.model.select_random_free_object(Type.CAR), Id(Type.CAR, 1))
        self.assertEqual(self.model.select_random_free_object(Type.GARAGE), Id(Type.GARAGE, 0))
        self.model.set_object_is_occuped(Id(Type.CAR, 1))
        self.assertIsNone(self.model.select_random_free_object(Type.CAR))
        self.assertEqual(self.model.select_random_free_object(), Id(Type.GARAGE, 0))

    def test_select_and_occupy_exhausts_storage_without_reuse(self):
        self.model.init_objects(range(5), Type.CAR)
        self.model.init_objects(range(3), Type.GARAGE)
        selected = set()
        for _ in range(8):
            object_id = self.model.select_random_free_object()
            self.assertIsNotNone(object_id)
            self.assertNotIn(object_id, selected)
            selected.add(object_id)
            self.model.set_object_is_occuped(object_id)
        self.assertIsNone(self.model.select_random_free_object())


if __name__ == "__main__":
    unittest.main()
