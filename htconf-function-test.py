#!/usr/bin/env python3
# coding:utf-8
import unittest
import htconf


class TestEscConf(unittest.TestCase):
    def test_no_escape(self):
        actual = htconf.esc_conf("hello")
        expect = "hello"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_escape_space(self):
        actual = htconf.esc_conf("hello world")
        expect = "\"hello world\""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_escape_quote(self):
        actual = htconf.esc_conf("hello\"world")
        expect = "\"hello\\\"world\""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_escape_backslash(self):
        actual = htconf.esc_conf("hello\\world")
        expect = "\"hello\\\\world\""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_escape_multiple_chars(self):
        actual = htconf.esc_conf("he\"llo\\w\"orl\\\"d")
        expect = "\"he\\\"llo\\\\w\\\"orl\\\\\\\"d\""
        self.assertEqual(expect, actual, "Result should match expected output")


class TestEscRegexp(unittest.TestCase):
    def test_no_escape(self):
        actual = htconf.esc_regexp("hello world")
        expect = "\"?hello world\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_regexp_dot(self):
        actual = htconf.esc_regexp("hello.worl.d")
        expect = "\"?hello\\.worl\\.d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_backslash(self):
        actual = htconf.esc_regexp("hello\\worl\\d")
        expect = "\"?hello\\\\worl\\\\d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_aster(self):
        actual = htconf.esc_regexp("hello*worl*d")
        expect = "\"?hello\\*worl\\*d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_plus(self):
        actual = htconf.esc_regexp("hello+worl+d")
        expect = "\"?hello\\+worl\\+d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_question(self):
        actual = htconf.esc_regexp("hello?worl?d")
        expect = "\"?hello\\?worl\\?d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_brackets(self):
        actual = htconf.esc_regexp("[hello[ ]world]")
        expect = "\"?\\[hello\\[ \\]world\\]\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_parentheses(self):
        actual = htconf.esc_regexp("(hello( )world)")
        expect = "\"?\\(hello\\( \\)world\\)\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_braces(self):
        actual = htconf.esc_regexp("{hello{ }world}")
        expect = "\"?\\{hello\\{ \\}world\\}\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_doll(self):
        actual = htconf.esc_regexp("hello\worl\d")
        expect = "\"?hello\\\worl\\\d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_tilde(self):
        actual = htconf.esc_regexp("hello^worl^d")
        expect = "\"?hello\\^worl\\^d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_verticalbar(self):
        actual = htconf.esc_regexp("hello|worl|d")
        expect = "\"?hello\\|worl\\|d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")


class TestGetIndent(unittest.TestCase):
    def test_space(self):
        actual = htconf.get_indent('   This is indented')
        expect = '   '
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_tab(self):
        actual = htconf.get_indent('		This is indented with tabs')
        expect = '		'
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_none(self):
        actual = htconf.get_indent('No indentation here.')
        expect = ''
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_mixed(self):
        actual = htconf.get_indent('    	Some spaces, but also tabs')
        expect = '    	'
        self.assertEqual(expect, actual, "Result should match expected output")


if __name__ == '__main__':
    unittest.main()
