import collections.abc
import copy
import random
import unittest

from frozendict import frozendict, FrozenOrderedDict


class TestImportCompatibility(unittest.TestCase):
    def test_imports_on_modern_python(self):
        import frozendict as fd_module
        self.assertTrue(hasattr(fd_module, 'frozendict'))
        self.assertTrue(hasattr(fd_module, 'FrozenOrderedDict'))

    def test_is_collections_abc_mapping(self):
        self.assertIsInstance(frozendict({}), collections.abc.Mapping)


class TestImmutability(unittest.TestCase):
    def setUp(self):
        self.f = frozendict({'a': 1, 'b': 2})

    def test_item_assignment_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.f['c'] = 3

    def test_item_deletion_raises_type_error(self):
        with self.assertRaises(TypeError):
            del self.f['a']

    def test_no_mutating_dict_methods(self):
        for name in ('pop', 'popitem', 'clear', 'update', 'setdefault'):
            self.assertFalse(hasattr(self.f, name))

    def test_copy_is_independent_with_replacements(self):
        g = self.f.copy(a=9, c=3)
        self.assertEqual(dict(g.items()), {'a': 9, 'b': 2, 'c': 3})
        self.assertEqual(dict(self.f.items()), {'a': 1, 'b': 2})
        self.assertIsNot(g, self.f)

    def test_constructor_copies_source_mapping(self):
        src = {'a': [1]}
        f = frozendict(src)
        src['b'] = 2
        self.assertNotIn('b', f)
        self.assertEqual(len(f), 1)


class TestEqualityAndHash(unittest.TestCase):
    def test_empty_hash_is_zero(self):
        self.assertEqual(hash(frozendict()), 0)

    def test_hash_matches_xor_of_pairs_oracle(self):
        d = {'a': 1, 'b': (2, 3), 'k': frozenset([1])}
        expected = 0
        for pair in d.items():
            expected ^= hash(pair)
        self.assertEqual(hash(frozendict(d)), expected)

    def test_hash_is_cached_and_stable(self):
        f = frozendict({'a': 1})
        self.assertEqual(hash(f), hash(f))

    def test_equal_maps_have_equal_hashes(self):
        rng = random.Random(0xC0FFEE)
        keys = [0, 1, -1, 'a', 'b', None, True, (1, 2), frozenset([1])]
        for _ in range(200):
            d = {k: rng.choice(keys) for k in rng.sample(keys, rng.randint(0, 6))}
            f1 = frozendict(d)
            f2 = frozendict(dict(d))
            self.assertEqual(f1, f2)
            self.assertEqual(f1, d)
            self.assertEqual(hash(f1), hash(f2))

    def test_unequal_maps_compare_unequal(self):
        self.assertNotEqual(frozendict({'a': 1}), frozendict({'a': 2}))
        self.assertNotEqual(frozendict({'a': 1}), 42)
        self.assertNotEqual(frozendict({'a': 1}), [])

    def test_usable_in_set_with_dedupe(self):
        s = {frozendict({'k': i}) for i in range(10)}
        for i in range(10):
            s.add(frozendict({'k': i}))
        self.assertEqual(len(s), 10)


class TestNestedValues(unittest.TestCase):
    def test_mutable_nested_values_are_unhashable(self):
        for value in ([1, 2], {'x': 1}, {1, 2}):
            f = frozendict({'k': value})
            with self.assertRaises(TypeError):
                hash(f)
            self.assertEqual(f, frozendict({'k': value}))

    def test_failed_hash_is_not_cached_as_success(self):
        f = frozendict({'a': [1]})
        with self.assertRaises(TypeError):
            hash(f)
        with self.assertRaises(TypeError):
            hash(f)

    def test_deep_nested_immutable_values_hash_and_compare(self):
        def make():
            return frozendict({
                'a': frozendict({'b': (1, frozendict({'c': 2}))})
            })
        f1, f2 = make(), make()
        self.assertEqual(f1, f2)
        self.assertEqual(hash(f1), hash(f2))
        self.assertEqual(len({f1, f2, frozendict({'a': 1})}), 2)


class TestInterfaceAndOrder(unittest.TestCase):
    def test_basic_mapping_interface(self):
        f = frozendict({'a': 1, 'b': 2})
        self.assertEqual(f['a'], 1)
        self.assertEqual(f.get('z', 7), 7)
        self.assertIn('a', f)
        self.assertNotIn('z', f)
        self.assertEqual(len(f), 2)
        self.assertTrue(f)
        self.assertFalse(frozendict())
        self.assertEqual(repr(f), "<frozendict {'a': 1, 'b': 2}>")

    def test_frozen_ordered_dict_keeps_order_and_type(self):
        od = FrozenOrderedDict([('z', 1), ('a', 2), ('m', 3)])
        self.assertEqual(list(od.keys()), ['z', 'a', 'm'])
        with self.assertRaises(TypeError):
            od['z'] = 9
        self.assertIsInstance(od, frozendict)
        self.assertIsInstance(od.copy(), FrozenOrderedDict)
        self.assertEqual(list(od.copy(x=9).keys()), ['z', 'a', 'm', 'x'])


if __name__ == '__main__':
    unittest.main()
