#!/usr/bin/env python3
# coding:utf-8
import unittest
import htconf


class TestEscConf(unittest.TestCase):
    def test_esc_conf_no_escape(self):
        actual = htconf.esc_conf("hello")
        expect = "hello"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_conf_space(self):
        actual = htconf.esc_conf("hello world")
        expect = "\"hello world\""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_conf_quote(self):
        actual = htconf.esc_conf("hello\"world")
        expect = "\"hello\\\"world\""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_conf_backslash(self):
        actual = htconf.esc_conf("hello\\world")
        expect = "\"hello\\\\world\""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_conf_multiple_chars(self):
        actual = htconf.esc_conf("he\"llo\\w\"orl\\\"d")
        expect = "\"he\\\"llo\\\\w\\\"orl\\\\\\\"d\""
        self.assertEqual(expect, actual, "Result should match expected output")


class TestEscRegexp(unittest.TestCase):
    def test_esc_regexp_no_escape(self):
        actual = htconf.esc_regexp("hello world")
        expect = "\"?hello world\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_dot(self):
        actual = htconf.esc_regexp("hello.worl.d")
        expect = "\"?hello\\.worl\\.d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_backslash(self):
        actual = htconf.esc_regexp("hello\\worl\\d")
        expect = "\"?hello\\\\worl\\\\d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_aster(self):
        actual = htconf.esc_regexp("hello*worl*d")
        expect = "\"?hello\\*worl\\*d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_plus(self):
        actual = htconf.esc_regexp("hello+worl+d")
        expect = "\"?hello\\+worl\\+d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_question(self):
        actual = htconf.esc_regexp("hello?worl?d")
        expect = "\"?hello\\?worl\\?d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_brackets(self):
        actual = htconf.esc_regexp("[hello[ ]world]")
        expect = "\"?\\[hello\\[ \\]world\\]\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_parentheses(self):
        actual = htconf.esc_regexp("(hello( )world)")
        expect = "\"?\\(hello\\( \\)world\\)\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_braces(self):
        actual = htconf.esc_regexp("{hello{ }world}")
        expect = "\"?\\{hello\\{ \\}world\\}\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_doll(self):
        actual = htconf.esc_regexp("hello\worl\d")
        expect = "\"?hello\\\worl\\\d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_tilde(self):
        actual = htconf.esc_regexp("hello^worl^d")
        expect = "\"?hello\\^worl\\^d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_esc_regexp_verticalbar(self):
        actual = htconf.esc_regexp("hello|worl|d")
        expect = "\"?hello\\|worl\\|d\"?"
        self.assertEqual(expect, actual, "Result should match expected output")


class TestGetIndent(unittest.TestCase):
    def test_get_indent_space(self):
        actual = htconf.get_indent('   This is indented')
        expect = '   '
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_get_indent_tab(self):
        actual = htconf.get_indent('		This is indented with tabs')
        expect = '		'
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_get_indent_none(self):
        actual = htconf.get_indent('No indentation here.')
        expect = ''
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_get_indent_mixed(self):
        actual = htconf.get_indent('    	Some spaces, but also tabs')
        expect = '    	'
        self.assertEqual(expect, actual, "Result should match expected output")


if __name__ == '__main__':
    unittest.main()
