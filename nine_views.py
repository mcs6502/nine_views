#! /usr/bin/env python

"""
nine_views.py: Prints the poem "Nine Views of Mount Fuji" by Mike Keith.
"""

import argparse
import re
import sys
import urllib.request

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"

# The number of views of Mt Fuji
VIEW_COUNT = 9

# The default character set for the poem
# This will be used for non-HTTP transports or where there is no charset header
DEFAULT_CHARSET = 'utf8'

# The non-breaking space character (used in poem's indents)
NBSP = '&nbsp;'

# A regex for retrieving the poem's title (could use <title> or <h1>)
title_re = re.compile('<h1>([^<].*)</h1>')

# A <span> element contains the author's name
author_re = re.compile(r'<(\w+)\s+class="author">([^<].*)</\1>')

# Each stanza begins with a pictorial view of Mount Fuji, so we use this feature
# to divide the web page into sections, with one section per stanza with the
# exception of the first section, which contains the beginning of document.
# NB this pattern will only work correctly if the view count is less than ten.
stanza_re = re.compile(
    f'<img\\s+src="[^"]*Fuji([1-{VIEW_COUNT}])\\.\\w+">')

# The regular expressions below define a simple scanner (lexer) for tokens
# that comprise a stanza -- namely, we have words and their delimiters.

# Word delimiters in a stanza -- whitespace, tags and the hyphen character
delim_re = re.compile(r'\s+|<[^<>]+>|-|\.|,|:|;|"|\?|\(|\)|' + NBSP)

# The characters that comprise a single word -- NB this includes the apostrophe!
word_re = re.compile("[\\w\']+")


def match_delim(s):
    return delim_re.match(s)


def match_word(s):
    return word_re.match(s)


# Returns the numeric value of the specified letter of the alphabet,
# or zero if the input value is invalid.
def char_code(c):
    n = ord(c) - 64
    return n if 0 < n <= 26 else 0


# Returns the numeric value of the specified word. This is calculated as a sum
# of values of its characters.
def word_code(word):
    return sum([char_code(c) for c in word.upper()])


# Returns True if the numeric value of the input word is divisible by nine.
def predicate_dee(word):
    n = word_code(word)
    return n % 9 == 0 and n != 0


# Returns True if the input word consists of exactly nine letters.
def predicate_ell(word):
    return len([c for c in word.upper() if char_code(c) != 0]) == 9


def read_poem(url, handler):
    with urllib.request.urlopen(url) as resource:
        charset = resource.headers.get_content_charset()
        if charset is None:
            charset = DEFAULT_CHARSET

        document = resource.read().decode(charset)

        title_match = title_re.search(document)
        if title_match is None:
            raise RuntimeError("Couldn't determine the title of the poem")

        author_match = author_re.search(document)
        if author_match is None:
            raise RuntimeError("Couldn't determine the author of the poem")

        # The <img> regex contains a capturing group for the index of the view;
        # consequently, the result of split() will contain an initial non-image
        # section (the title and author) followed by pairs of (index, stanza)
        sections = stanza_re.split(document)
        if not sections or len(sections) <= 1:
            raise RuntimeError("Couldn't find any stanzas")

        title = title_match.group(1)
        author = author_match.group(2)

        handler.begin_poem(title, author)

        num_stanzas = 0
        # Skip the first section containing the title and author's name, and
        # iterate by pairs (view index, stanza)
        for i in range(1, len(sections), 2):
            m = int(sections[i])
            n = num_stanzas + 1
            if m != n:
                raise RuntimeError(
                    "Unexpected stanza (got {} but needed {})".format(m, n))
            num_stanzas = n
            stanza = sections[i + 1]

            # Scan the stanza decomposing it into (interpretable) tokens and
            # passing them on to the handler.
            j = 0
            k = VIEW_COUNT * VIEW_COUNT
            handler.begin_stanza()
            while True:
                if stanza == '':  # exit the loop once we are done reading
                    break
                delim_match = delim_re.match(stanza)
                if delim_match:
                    stanza = stanza[delim_match.end():]
                    delim = delim_match.group()
                    handler.on_delimiter(delim)
                    continue

                word_match = word_re.match(stanza)
                if word_match:
                    # Exit the loop if we have seen enough words.
                    # We do this here rather than after printing
                    # the word -- this is so that punctuation that might
                    # follow the word is not lost.
                    if j >= k:
                        break
                    stanza = stanza[word_match.end():]
                    word = word_match.group()
                    handler.word(word)
                    j += 1
                    continue

                raise RuntimeError(
                    "Unable to parse stanza at \"{}\"".format(
                        stanza[:32]))

            handler.end_stanza()

        if num_stanzas != VIEW_COUNT:
            raise RuntimeError(
                "Found {} stanzas (need {})".format(num_stanzas, VIEW_COUNT))

        handler.end_poem()


class Printer(object):
    """The Printer class implements a simple poem handler that pretty-prints
     poem text to the console"""

    def __init__(self, writer=sys.stdout):
        self.writer = writer
        self.no_space = False

    def reset_line_state(self):
        self.no_space = True

    def print(self, msg=None, end='\n'):
        if msg is not None:
            self.writer.write(msg)
        self.writer.write(end)

    def print_space(self):
        self.print('', end=' ')

    def begin_poem(self, title, author):
        self.print(title)
        self.print()
        self.print(author)
        self.print()

    def end_poem(self):
        pass

    def begin_stanza(self):
        self.reset_line_state()

    def end_stanza(self):
        self.print()
        self.print()

    def on_delimiter(self, delim):
        if delim == '-' or delim == '"' \
                or delim == '.' or delim == ',' \
                or delim == ':' or delim == ';' \
                or delim == '(' or delim == ')' \
                or delim == '?':
            if delim == '(' and not self.no_space:
                self.print_space()
            # print these without space at end
            # because the following word will
            # have one
            self.print(delim, end='')
            self.no_space = delim == '-' or delim == '(' \
                            or delim == '"' and self.no_space  # opening quote
        elif delim == NBSP:
            self.print_space()
            self.no_space = True
        elif delim == '<p>' or delim == '<br />':
            self.print()
            self.no_space = True

    def word(self, word):
        if not self.no_space:
            self.print(' ', end='')
        self.no_space = False
        self.print(word, end='')


class Decoder(object):
    """The Decoder class implements a decoder for constraints in the Nine Views
    of Mount Fuji and outputs two bitmaps (one per constraint) containing ones
    in those positions where the corresponding word satistied the constraint"""

    def __init__(self, writer=sys.stdout):
        self.writer = writer
        self.dee_flags = bytearray()
        self.ell_flags = bytearray()

    def reset_flags(self):
        self.dee_flags.clear()
        self.ell_flags.clear()

    def as_str(self, flags):
        return ''.join(chr(c) for c in flags)

    def print(self, msg=None, end='\n'):
        if msg is not None:
            self.writer.write(msg)
        self.writer.write(end)

    def print_flags(self, name, flags):
        print(f'{name}:{self.as_str(flags)}b')

    def begin_poem(self, title, author):
        self.reset_flags()

    def end_poem(self):
        self.print_flags('d', self.dee_flags)
        self.print_flags('l', self.ell_flags)

    def begin_stanza(self):
        pass

    def end_stanza(self):
        pass

    def on_delimiter(self, delim):
        pass

    def word(self, word):
        if word is None:
            raise RuntimeError('nil word')
        t = ord('1')
        f = ord('0')
        self.dee_flags.append(t if predicate_dee(word) else f)
        self.ell_flags.append(t if predicate_ell(word) else f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prints or decodes the poem '
                                                 '"Nine Views of Mount Fuji".')
    parser.add_argument('-d', '--decode', action='store_true',
                        help='decode poem text according to constraints')
    parser.add_argument('poem_url', metavar='URL',
                        help='address of the web page with poem\'s text')
    args = parser.parse_args()
    handler = Decoder() if args.decode else Printer()
    read_poem(args.poem_url, handler)
