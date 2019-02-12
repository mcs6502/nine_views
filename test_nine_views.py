import unittest

from nine_views import match_delim, match_word

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"


class LexerTest(unittest.TestCase):
    def assert_delim(self, s, d):
        m = match_delim(s)
        if d is None:
            self.assertIsNone(m)
        else:
            self.assertTrue(m)
            self.assertEquals(d, m.group())
        return m

    def assert_word(self, s, w):
        m = match_word(s)
        if w is None:
            self.assertIsNone(m)
        else:
            self.assertTrue(m)
            self.assertEquals(w, m.group())
        return m

    def assert_delims(self, s, delims, rest):
        for d in delims:
            m = self.assert_delim(s, d)
            s = s[m.end():]
        self.assertEquals(rest, s)

    def test_delims(self):
        self.assert_delim('</div>', '</div>')

        self.assert_delims("""?</div>

<br />;

<p>"The gifted artist""", ['?', '</div>', """

""", '<br />', ';', """

""", '<p>', '"'], 'The gifted artist')

        self.assert_delims(""". </p>,

(<p>)&nbsp;:&nbsp;""", ['.', ' ', '</p>', ',', """

""", '(', '<p>', ')', '&nbsp;', ':', '&nbsp;'], '')

    def test_words(self):
        self.assert_word("Fuji's", "Fuji's")


if __name__ == '__main__':
    unittest.main()
