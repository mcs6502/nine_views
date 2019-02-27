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

TOP_VIEW = 'top'
FRONT_VIEW = 'front'
RIGHT_VIEW = 'right'
BOTTOM_VIEW = 'bottom'
BACK_VIEW = 'back'
LEFT_VIEW = 'left'

X = 2
Y = 1
Z = 0

TRANSPOSE = "transpose"

BOOLEAN_LIST_REGEX = '([01]+)b'


class StandardViewpoint(object):
    def __init__(self, view_axis, tweaks):
        self.view_axis = view_axis
        self.tweaks = tweaks

    def project(self, block):
        view = np.apply_along_axis(np.max, self.view_axis, block)
        for tweak in self.tweaks:
            if tweak == TRANSPOSE:
                view = np.transpose(view)
            else:
                view = np.flip(view, tweak)
        return view


class Projector(object):
    def __init__(self):
        views = {TOP_VIEW: StandardViewpoint(Y, [0]),
                 FRONT_VIEW: StandardViewpoint(Z, []),
                 RIGHT_VIEW: StandardViewpoint(X, [TRANSPOSE, 1]),
                 BOTTOM_VIEW: StandardViewpoint(Y, []),
                 BACK_VIEW: StandardViewpoint(Z, [1]),
                 LEFT_VIEW: StandardViewpoint(X, [TRANSPOSE])}
        self.views = views

    def project(self, block, view_name):
        view = self.get_view(view_name)
        return view.project(block)

    def get_view(self, view_name):
        view = self.views[view_name]
        if view is None:
            raise RuntimeError(f'Unknown view name: "${view_name}"')
        return view

    def get_images(self, block, view_names, tiles=None):
        if tiles is None:
            tiles = ['  ', 'XX']
        for view_name in view_names:
            view = self.project(block, view_name)
            rows = np.flip(view, 0)
            yield "\n".join([''.join([tiles[c] for c in r]) for r in rows])


def take_n(n, s):
    """Take n characters from string s"""
    m = len(s)  # the actual number of characters in s
    if m == n:
        return s
    a, b = divmod(n, m)  # repeat s 'a' times and add 'b' chars to get size n
    return s * a + s[:b]


def build_block(bits, dims):
    """Parse a string of 0/1 bits into a n-dimensional list of flags"""
    m = int(np.prod(dims))  # the number of bits required to cover dims
    s = take_n(m, bits)  # gets the string of the right size
    o = ord('0')
    a = np.asarray([ord(c) - o for c in s], dtype=np.uint8)
    return a.reshape(dims)


class BlockBuilder(object):

    def __init__(self, dims=None):
        self.dims = dims
        # a bitmap is a string of '0' and '1' characters ending with a 'b'
        self.bitmap_re = re.compile(BOOLEAN_LIST_REGEX)

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
    projector = Projector()
    continued = False
    for line in fileinput.input(files):
        blocks = builder.parse_blocks(line)
        for block in blocks:
            for image in projector.get_images(block, views):
                if continued:
                    print("\n\n")
                else:
                    continued = True
                print(image)


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
