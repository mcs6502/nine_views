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


def build_block(bits):
    """Parse a string of 0/1 bits into a three-dimensional list of booleans"""
    n = len(bits)  # the number of bits in the bitmap
    # dimensions of the block -- for now assume it is a cube
    a = b = c = int(round(n ** (1. / 3)))
    return np.asarray([c == '1' for c in bits]).reshape([a, b, c])


def print_bitmap_views(block, views):
    print(block)


def print_views(files, views):
    # a bitmap is a string of '0' and '1' characters ending with a 'b'
    bitmap_re = re.compile('([01]+)b')
    for line in fileinput.input(files):
        for bitmap_match in bitmap_re.finditer(line):
            # the group as defined in re drops the 'b' keeping just the bits
            bits = bitmap_match.group(1)
            block = build_block(bits)
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
    print_views(args.files, args.views)
