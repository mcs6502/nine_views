#! /usr/bin/env python

"""
nine_views.py: Prints the poem "Nine Views of Mount Fuji" by Mike Keith.
"""

import re
import urllib.request

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"

# The location to download the text of the poem from
poem_url = 'http://www.farragoswainscot.com/2009/11/nine_views.html'

# Base URL for the views of Mt Fuji
fuji_url = 'http://www.farragoswainscot.com/2009/11/fuji/'

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
    '<img\\s+src="' + fuji_url + (r'Fuji([1-{}])\.\w+">'.format(VIEW_COUNT)))

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


def read_poem(url):
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

        print(title)
        print()
        print(author)
        print()

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
            # pretty-printing its text to the console.
            j = 0
            k = VIEW_COUNT * VIEW_COUNT
            l = 0  # line length in words
            no_space = False
            while True:
                if stanza == '':  # exit the loop once we are done reading
                    break
                delim_match = delim_re.match(stanza)
                if delim_match:
                    stanza = stanza[delim_match.end():]
                    delim = delim_match.group()
                    if delim == '-' or delim == '"' \
                            or delim == '.' or delim == ',' \
                            or delim == ':' or delim == ';' \
                            or delim == '(' or delim == ')' \
                            or delim == '?':
                        if delim == '(' and l > 0:
                            print_space()
                        # print these without space at end
                        # because the following word will
                        # have one
                        print(delim, end='')
                        no_space = delim == '-' or delim == '('
                    elif delim == NBSP:
                        print_space()
                        no_space = True
                    elif delim == '<p>' or delim == '<br />':
                        l = 0
                        print()
                        no_space = True
                    continue

                word = word_re.match(stanza)
                if word:
                    # Exit the loop if we have seen enough words.
                    # We do this here rather than after printing
                    # the word -- this is so that punctuation that might
                    # follow the word is not lost.
                    if (j >= k):
                        break
                    stanza = stanza[word.end():]
                    if l > 0 and not no_space:
                        print(' ', end='')
                    no_space = False
                    print(word.group(), end='')
                    j += 1
                    l += 1
                    continue

                raise RuntimeError(
                    "Unable to parse stanza at \"{}\"".format(
                        stanza[:32]))

            print()
            print()

        if num_stanzas != VIEW_COUNT:
            raise RuntimeError(
                "Found {} stanzas (need {})".format(num_stanzas, VIEW_COUNT))


def print_space():
    print('', end=' ')


if __name__ == '__main__':
    read_poem(poem_url)
