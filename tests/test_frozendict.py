import operator
import random
import unittest
from collections.abc import Mapping

from frozendict import frozendict, FrozenOrderedDict


class TestImmutability(unittest.TestCase):
    def test_setitem_raises(self):
        fd = frozendict(a=1)
        with self.assertRaises(TypeError):
            operator.setitem(fd, 'a', 2)
        self.assertEqual(dict(fd), {'a': 1})

    def test_delitem_raises(self):
        fd = frozendict(a=1)
        with self.assertRaises(TypeError):
            operator.delitem(fd, 'a')
        self.assertEqual(dict(fd), {'a': 1})


class TestEqualityAndHash(unittest.TestCase):
    def test_seeded_differential_round(self):
        rng = random.Random(93)
        for _ in range(200):
            keys = rng.sample(range(12), k=rng.randrange(6))
            items = [(f'key{k}', (k, rng.randint(-100, 100))) for k in keys]
            shuffled = items[:]
            rng.shuffle(shuffled)
            fd1, fd2 = frozendict(items), frozendict(shuffled)
            self.assertEqual(fd1, dict(items))
            self.assertEqual(fd1, fd2)
            self.assertEqual(hash(fd1), hash(fd2))
            oracle = 0
            for key, value in dict(items).items():
                oracle ^= hash((key, value))
            self.assertEqual(hash(fd1), oracle)

    def test_inequality(self):
        self.assertNotEqual(frozendict(a=1), frozendict(a=2))
        self.assertNotEqual(frozendict(a=1), {'a': 1, 'b': 2})

    def test_hash_cached_stable(self):
        fd = frozendict(a=1, b=2)
        self.assertEqual(hash(fd), hash(fd))

    def test_copy_is_equal(self):
        fd = frozendict(a=1)
        self.assertEqual(fd.copy(), fd)
        self.assertEqual(fd.copy(b=2), frozendict(a=1, b=2))


class TestNestedValues(unittest.TestCase):
    def test_unhashable_nested_value_hash_raises(self):
        with self.assertRaises(TypeError):
            hash(frozendict(a=[1, 2]))

    def test_unhashable_nested_value_equality(self):
        self.assertEqual(frozendict(a=[1, 2]), frozendict(a=[1, 2]))
        self.assertNotEqual(frozendict(a=[1, 2]), frozendict(a=[1, 3]))

    def test_nested_frozendict_hashable(self):
        inner = frozendict(x=1)
        self.assertEqual(hash(frozendict(a=inner)), hash(frozendict(a=inner)))


class TestMappingInterface(unittest.TestCase):
    def test_mapping_abc(self):
        fd = frozendict(x=1, y=2)
        self.assertIsInstance(fd, Mapping)
        self.assertEqual(set(fd.keys()), {'x', 'y'})
        self.assertEqual(sorted(fd.values()), [1, 2])
        self.assertEqual(set(fd.items()), {('x', 1), ('y', 2)})
        self.assertEqual(fd.get('z', 7), 7)
        self.assertEqual(len(fd), 2)
        self.assertIn('x', fd)

    def test_frozen_ordered_dict_keeps_order(self):
        fod = FrozenOrderedDict([('b', 1), ('a', 2), ('c', 3)])
        self.assertEqual(list(fod), ['b', 'a', 'c'])


if __name__ == '__main__':
    unittest.main()
