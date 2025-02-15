import unittest
import fastdisjointset

###############################################################################
# Test cases for the StaticDisjointSet (when constructed with an integer n)
###############################################################################


class TestStaticDisjointSet(unittest.TestCase):
    def setUp(self):
        # Use the factory: passing an integer returns a StaticDisjointSet.
        self.ds = fastdisjointset.DisjointSet(5)

    def test_initial_find(self):
        # Initially, each element should be its own representative.
        for i in range(5):
            self.assertEqual(
                self.ds.find(i), i, msg=f'Element {i} should initially be its own root.'
            )

    def test_index_error(self):
        with self.assertRaises(IndexError):
            self.ds.find(-1)
        with self.assertRaises(IndexError):
            self.ds.find(5)
        with self.assertRaises(IndexError):
            self.ds.union(0, 5)

    def test_union_and_match(self):
        self.assertFalse(
            self.ds.match(0, 1),
            msg='Elements 0 and 1 should not be connected initially.',
        )
        self.ds.union(0, 1)
        self.assertTrue(
            self.ds.match(0, 1), msg='Elements 0 and 1 should be connected after union.'
        )
        self.ds.union(1, 2)
        self.assertTrue(
            self.ds.match(0, 2),
            msg='Elements 0 and 2 should be connected after chained unions.',
        )
        self.assertFalse(
            self.ds.match(3, 4),
            msg='Elements 3 and 4 should be in different sets initially.',
        )

    def test_sets(self):
        expected_initial = frozenset(
            [
                frozenset([0]),
                frozenset([1]),
                frozenset([2]),
                frozenset([3]),
                frozenset([4]),
            ]
        )
        self.assertEqual(
            self.ds.sets(),
            expected_initial,
            msg='Initial grouping should have each element in its own set.',
        )

        self.ds.union(0, 1)
        self.ds.union(1, 2)
        self.ds.union(3, 4)
        expected_groups = frozenset([frozenset([0, 1, 2]), frozenset([3, 4])])
        self.assertEqual(
            self.ds.sets(),
            expected_groups,
            msg='Sets grouping did not match expected groups after unions.',
        )


###############################################################################
# Test cases for the DynamicDisjointSet (when constructed with n=None or no argument)
###############################################################################


class TestDynamicDisjointSet(unittest.TestCase):
    def setUp(self):
        # Use the factory: passing None returns a DynamicDisjointSet.
        self.ds = fastdisjointset.DisjointSet(None)

    def test_find_new_element(self):
        # For a new element, find should return the element itself.
        result = self.ds.find('a')
        self.assertEqual(
            result, 'a', msg="New element's representative should be itself."
        )

    def test_union_and_match_dynamic(self):
        self.assertFalse(
            self.ds.match('apple', 'banana'),
            msg="Elements 'apple' and 'banana' should not be connected initially.",
        )
        self.ds.union('apple', 'banana')
        self.assertTrue(
            self.ds.match('apple', 'banana'),
            msg="Elements 'apple' and 'banana' should be connected after union.",
        )
        self.ds.union('banana', 'cherry')
        self.assertTrue(
            self.ds.match('apple', 'cherry'),
            msg="Elements 'apple' and 'cherry' should be connected after chained unions.",
        )
        self.assertFalse(
            self.ds.match('apple', 'date'),
            msg="'apple' and 'date' should not be connected unless unioned.",
        )

    def test_sets_dynamic(self):
        keys = ['x', 'y', 'z', 'w']
        for k in keys:
            self.ds.find(k)

        expected_initial = frozenset({frozenset([k]) for k in keys})
        self.assertEqual(
            self.ds.sets(),
            expected_initial,
            msg='Each key should initially be its own set.',
        )

        self.ds.union('x', 'y')
        self.ds.union('z', 'w')
        expected_groups = frozenset([frozenset(['x', 'y']), frozenset(['z', 'w'])])
        self.assertEqual(
            self.ds.sets(),
            expected_groups,
            msg='Dynamic sets grouping did not match expected groups after unions.',
        )

    def test_repeated_union(self):
        self.ds.union('a', 'b')
        self.ds.union('a', 'b')
        self.ds.union('b', 'a')
        self.assertTrue(
            self.ds.match('a', 'b'),
            msg="Repeated unions should not affect the connectivity of 'a' and 'b'.",
        )


###############################################################################
# Test the factory behavior of DisjointSet
###############################################################################


class TestDisjointSetFactory(unittest.TestCase):
    def test_factory_static(self):
        # When an integer is supplied, we should get a StaticDisjointSet.
        ds = fastdisjointset.DisjointSet(10)
        # We expect the 'find' method to exist (and StaticDisjointSet uses integer indices)
        self.assertTrue(hasattr(ds, 'find'))
        self.assertEqual(ds.find(0), 0)
        with self.assertRaises(IndexError):
            ds.find(10)

    def test_factory_dynamic(self):
        # When None is supplied, we should get a DynamicDisjointSet.
        ds = fastdisjointset.DisjointSet(None)
        self.assertTrue(hasattr(ds, 'find'))
        self.assertEqual(ds.find('test'), 'test')

    def test_factory_default(self):
        # When nothing is supplied, we should get a DynamicDisjointSet.
        ds = fastdisjointset.DisjointSet()
        self.assertTrue(hasattr(ds, 'find'))
        self.assertEqual(ds.find('test'), 'test')

    def test_version(self):
        version = tuple(map(int, fastdisjointset.__version__.split('.')))
        self.assertTrue(version > (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
