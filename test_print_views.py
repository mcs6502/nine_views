import unittest

import numpy as np

from print_views import build_block

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"


class BlockTest(unittest.TestCase):
    def test_build_block(self):
        np.testing.assert_array_equal([
            [[False, False, False], [False, False, True], [False, True, False]],
            [[False, True, True], [True, False, False], [True, False, True]],
            [[True, True, False], [True, True, True], [False, False, False]]
        ], build_block('000001010011100101110111000'))


if __name__ == '__main__':
    unittest.main()
