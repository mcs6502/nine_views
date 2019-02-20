import unittest

import numpy as np

from print_views import BlockBuilder, build_block

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"

T = True

F = False


def assert_array_equal(a, b):
    np.testing.assert_array_equal(a, b)


class BlockBuilderTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BlockBuilderTest, self).__init__(*args, **kwargs)

        self.input_3 = '000001010011100101110111000b'
        self.array_3 = [
            [[False, False, False], [False, False, True], [False, True, False]],
            [[False, True, True], [True, False, False], [True, False, True]],
            [[True, True, False], [True, True, True], [False, False, False]]
        ]

        self.input_2 = '00011011b'
        self.array_2 = [
            [[False, False], [False, True]],
            [[True, False], [True, True]]
        ]

    def test_build_block(self):
        bits = self.input_3[:-1]
        dims = [3, 3, 3]
        assert_array_equal(self.array_3, build_block(bits, dims))

    def test_parse_cube(self):
        builder = BlockBuilder()
        blocks = builder.parse_blocks(f"({self.input_3}; {self.input_2})")
        assert_array_equal(self.array_3, next(blocks))
        assert_array_equal(self.array_2, next(blocks))

    def test_parse_rect(self):
        builder = BlockBuilder([2, 4])
        blocks = builder.parse_blocks(f"{self.input_2} {self.input_3}")
        array_a = [[F, F, F, T], [T, F, T, T]]
        assert_array_equal(array_a, next(blocks))
        array_b = [[F, F, F, F], [F, T, F, T]]  # truncated input_3
        assert_array_equal(array_b, next(blocks))

    @staticmethod
    def test_parse_short_input():
        builder = BlockBuilder([2, 3, 4])
        blocks = builder.parse_blocks('0010101b')  # will replicate input
        a = [[[F, F, T, F], [T, F, T, F], [F, T, F, T]],
             [[F, T, F, F], [T, F, T, F], [T, F, F, T]]]
        assert_array_equal(a, next(blocks))


if __name__ == '__main__':
    unittest.main()
