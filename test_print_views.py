import unittest

import numpy as np

from print_views import BlockBuilder, build_block, Projector, TOP_VIEW, \
    FRONT_VIEW, RIGHT_VIEW, \
    BOTTOM_VIEW, BACK_VIEW, LEFT_VIEW

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"

T = 1

F = 0


def assert_array_equal(a, b):
    np.testing.assert_array_equal(a, b)


class BlockBuilderTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BlockBuilderTest, self).__init__(*args, **kwargs)

        self.input_3 = '000001010011100101110111000b'
        self.array_3 = [
            [[F, F, F], [F, F, T], [F, T, F]],
            [[F, T, T], [T, F, F], [T, F, T]],
            [[T, T, F], [T, T, T], [F, F, F]]
        ]

        self.input_2 = '00011011b'
        self.array_2 = [
            [[F, F], [F, T]],
            [[T, F], [T, T]]
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


class StandardViewpointTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(StandardViewpointTest, self).__init__(*args, **kwargs)
        self.projector = Projector()
        self.block = build_block('000000101000110111100000000b', [3, 3, 3])

    def create_viewpoint(self, view_name):
        return self.projector.get_view(view_name)

    def test_get_view(self):
        self.assert_view([[T, F, F], [T, T, T], [T, F, T]], TOP_VIEW)
        self.assert_view([[T, F, F], [T, T, F], [T, T, T]], FRONT_VIEW)
        self.assert_view([[T, F, F], [F, T, F], [F, T, T]], RIGHT_VIEW)
        self.assert_view([[T, F, T], [T, T, T], [T, F, F]], BOTTOM_VIEW)
        self.assert_view([[F, F, T], [F, T, T], [T, T, T]], BACK_VIEW)
        self.assert_view([[F, F, T], [F, T, F], [T, T, F]], LEFT_VIEW)

    def test_projector(self):
        i = self.projector.get_images(self.block, TOP_VIEW)
        image = next(i)
        self.assertEqual("XX  XX\nXXXXXX\nXX    ", image)

    def assert_view(self, expected_view, view_name):
        viewpoint = self.create_viewpoint(view_name)
        view = viewpoint.project(self.block)
        assert_array_equal(view, expected_view)


class ProjectorTest(unittest.TestCase):
    def test_parse_aspect(self):
        projector = Projector()
        self.assertRaises(RuntimeError, projector.parse_aspect, None)
        self.assertRaises(RuntimeError, projector.parse_aspect, '')
        self.assertRaises(RuntimeError, projector.parse_aspect, 'a b+')
        self.assertEqual(projector.parse_aspect('foo'), ('foo', None))
        self.assertEqual(projector.parse_aspect('bar-1'), ('bar', '-1'))
        self.assertEqual(projector.parse_aspect('baz+123'), ('baz', '+123'))


if __name__ == '__main__':
    unittest.main()
