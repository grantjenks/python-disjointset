#!/usr/bin/env python3
import unittest
import disjointset

###############################################################################
# Test cases for the StaticDisjointSet (pre-allocated with a fixed n)
###############################################################################


class TestStaticDisjointSet(unittest.TestCase):
    def setUp(self):
        # Create a static disjoint set with 5 elements: 0, 1, 2, 3, 4.
        self.ds = disjointset.StaticDisjointSet(5)

    def test_initial_find(self):
        # Initially, each element should be its own representative.
        for i in range(5):
            self.assertEqual(
                self.ds.find(i), i, msg=f'Element {i} should initially be its own root.'
            )

    def test_index_error(self):
        # Accessing an index out of range should raise an IndexError.
        with self.assertRaises(IndexError):
            self.ds.find(-1)
        with self.assertRaises(IndexError):
            self.ds.find(5)
        with self.assertRaises(IndexError):
            self.ds.union(0, 5)

    def test_union_and_match(self):
        # Test that union and match work as expected.
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
        # Test the sets() method.
        # Initially, every element is in its own set.
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

        # After a few unions, verify that groups are correct.
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
# Test cases for the DynamicDisjointSet (dynamic keys, not pre-allocated)
###############################################################################


class TestDynamicDisjointSet(unittest.TestCase):
    def setUp(self):
        self.ds = disjointset.DynamicDisjointSet()

    def test_find_new_element(self):
        # For a new element, find should return the element itself and add it.
        result = self.ds.find('a')
        self.assertEqual(
            result, 'a', msg="New element's representative should be itself."
        )

    def test_union_and_match_dynamic(self):
        # Test union and match with arbitrary (non-integer) keys.
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
        # Ensure that sets() returns proper groupings for dynamic keys.
        keys = ['x', 'y', 'z', 'w']
        # Calling find on each key initializes them.
        for k in keys:
            self.ds.find(k)
        expected_initial = frozenset({frozenset([k]) for k in keys})
        self.assertEqual(
            self.ds.sets(),
            expected_initial,
            msg='Each key should initially be its own set.',
        )

        # Perform unions and check grouping.
        self.ds.union('x', 'y')
        self.ds.union('z', 'w')
        expected_groups = frozenset([frozenset(['x', 'y']), frozenset(['z', 'w'])])
        self.assertEqual(
            self.ds.sets(),
            expected_groups,
            msg='Sets grouping did not match expected dynamic groups after unions.',
        )

    def test_repeated_union(self):
        # Repeated unions on the same keys should have no adverse effect.
        self.ds.union('a', 'b')
        self.ds.union('a', 'b')
        self.ds.union('b', 'a')
        self.assertTrue(
            self.ds.match('a', 'b'),
            msg="Repeated unions should not affect the connectivity of 'a' and 'b'.",
        )


if __name__ == '__main__':
    unittest.main()
