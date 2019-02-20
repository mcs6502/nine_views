#! /usr/bin/env python

"""
print_views.py: Prints a two-dimensional view of a 3D bitmap on the console.
"""

import argparse
import fileinput
import re

import numpy as np

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"


def take_n(n, s):
    """Take n characters from string s"""
    m = len(s)  # the actual number of bits
    if m == n:
        return s
    a, b = divmod(n, m)  # repeat s 'a' times and add 'b' chars to get size n
    return s * a + s[:b]


def build_block(bits, dims):
    """Parse a string of 0/1 bits into a n-dimensional list of booleans"""
    m = int(np.prod(dims))  # the number of bits required to cover dims
    s = take_n(m, bits)  # gets the string of the right size
    a = np.asarray([c != '0' for c in s])
    return a.reshape(dims)


def print_bitmap_views(block, views):
    print(block)


class BlockBuilder(object):

    def __init__(self, dims=None):
        self.dims = dims
        # a bitmap is a string of '0' and '1' characters ending with a 'b'
        self.bitmap_re = re.compile('([01]+)b')

    def block_dims(self, bits):
        if self.dims is not None:
            return self.dims
        n = len(bits)  # the number of bits in the bitmap
        # dimensions of the block -- for now assume it is a cube
        m = int(round(n ** (1. / 3)))
        return [m, m, m]

    def parse_blocks(self, line):
        for bitmap_match in self.bitmap_re.finditer(line):
            # the group as defined in re drops the 'b' keeping just the bits
            bits = bitmap_match.group(1)
            dims = self.block_dims(bits)
            yield build_block(bits, dims)


def print_views(builder, files, views):
    for line in fileinput.input(files):
        blocks = builder.parse_blocks(line)
        for block in blocks:
            print_bitmap_views(block, views)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prints a two-dimensional view'
                                                 ' of a 3D bitmap on the'
                                                 ' console.')
    parser.add_argument('views', nargs='+', metavar='VIEW',
                        help='view bitmap along axis -- for example, "1x"'
                             ' selects the view of the first bitmap along its'
                             ' x axis (use uppercase letter for mirror image)')
    parser.add_argument('files', nargs='*', metavar='FILE',
                        help='input files to read (if empty then read stdin)')
    args = parser.parse_args()
    print_views(BlockBuilder(), args.files, args.views)
