import unittest

from nine_views import match_delim, match_word, predicate_dee, predicate_ell, \
    word_code

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"


class DecoderTest(unittest.TestCase):
    def test_word_code(self):
        self.assertEqual(21, word_code('abcdef'))
        self.assertEqual(21, word_code('a, b, c, d, e, f!'))

    def test_predicate_dee(self):
        self.assertFalse(predicate_dee('a'))  # 1
        self.assertFalse(predicate_dee('A'))  # 1
        self.assertTrue(predicate_dee('i'))  # 9
        self.assertTrue(predicate_dee('I'))  # 9
        self.assertFalse(predicate_dee(''))

    def test_predicate_ell(self):
        self.assertTrue(predicate_ell('gimme_nine'))
        self.assertTrue(predicate_ell('gimmeNine'))
        self.assertTrue(predicate_ell('e - learning'))
        self.assertTrue(predicate_ell('elearning'))
        self.assertFalse(predicate_ell('learning'))
        self.assertFalse(predicate_ell('?'))
        self.assertFalse(predicate_ell(''))


class LexerTest(unittest.TestCase):
    def assert_delim(self, s, d):
        m = match_delim(s)
        if d is None:
            self.assertIsNone(m)
        else:
            self.assertTrue(m)
            self.assertEqual(d, m.group())
        return m

    def assert_word(self, s, w):
        m = match_word(s)
        if w is None:
            self.assertIsNone(m)
        else:
            self.assertTrue(m)
            self.assertEqual(w, m.group())
        return m

    def assert_delims(self, s, delims, rest):
        for d in delims:
            m = self.assert_delim(s, d)
            s = s[m.end():]
        self.assertEqual(rest, s)

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
