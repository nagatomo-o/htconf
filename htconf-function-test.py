#!/usr/bin/env python3
# coding:utf-8
import unittest
import htconf

class TestEsc(unittest.TestCase):
    def test_noEscape(self):
        actual=htconf.esc("hello")
        expect="hello"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_escapeSpace(self):
        actual=htconf.esc("hello world")
        expect="\"hello world\""
        self.assertEqual(expect,actual,"Result should match expected output")


    def test_escapeQuote(self):
        actual=htconf.esc("hello\"world")
        expect="\"hello\\\"world\""
        self.assertEqual(expect,actual,"Result should match expected output")


    def test_escapeBackslash(self):
        actual=htconf.esc( "hello\\world")
        expect="\"hello\\\\world\""
        self.assertEqual(expect,actual,"Result should match expected output")


    def test_escapeMultipleChars(self):
        actual=htconf.esc("he\"llo\\w\"orl\\\"d")
        expect="\"he\\\"llo\\\\w\\\"orl\\\\\\\"d\""
        self.assertEqual(expect,actual,"Result should match expected output")

class TestRegexp(unittest.TestCase):
    def test_noEscape(self):
        actual=htconf.regexp("hello world")
        expect="\"?hello world\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_testRegexpDot(self):
        actual=htconf.regexp("hello.worl.d")
        expect="\"?hello\\.worl\\.d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_backslash(self):
        actual=htconf.regexp("hello\\worl\\d")
        expect="\"?hello\\\\worl\\\\d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_aster(self):
        actual=htconf.regexp( "hello*worl*d")
        expect="\"?hello\\*worl\\*d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_testRegexpPlus(self):
        actual=htconf.regexp("hello+worl+d")
        expect="\"?hello\\+worl\\+d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_question(self):
        actual=htconf.regexp("hello?worl?d")
        expect="\"?hello\\?worl\\?d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_brackets(self):
        actual=htconf.regexp("[hello[ ]world]")
        expect="\"?\\[hello\\[ \\]world\\]\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_parentheses(self):
        actual=htconf.regexp("(hello( )world)")
        expect="\"?\\(hello\\( \\)world\\)\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_braces(self):
        actual=htconf.regexp("{hello{ }world}")
        expect="\"?\\{hello\\{ \\}world\\}\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_doll(self):
        actual=htconf.regexp("hello\worl\d")
        expect="\"?hello\\\worl\\\d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_tilde(self):
        actual=htconf.regexp("hello^worl^d")
        expect="\"?hello\\^worl\\^d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_verticalbar(self):
        actual=htconf.regexp("hello|worl|d")
        expect="\"?hello\\|worl\\|d\"?"
        self.assertEqual(expect,actual,"Result should match expected output")

class TestGetIndent(unittest.TestCase):
    def test_space(self):
        actual=htconf.get_indent('   This is indented')
        expect='   '
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_tab(self):
        actual=htconf.get_indent('		This is indented with tabs')
        expect='		'
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_none(self):
        actual=htconf.get_indent('No indentation here.')
        expect=''
        self.assertEqual(expect,actual,"Result should match expected output")

    def test_mixed(self):
        actual=htconf.get_indent( '    	Some spaces, but also tabs')
        expect='    	'
        self.assertEqual(expect,actual,"Result should match expected output")

if __name__ == '__main__':
    unittest.main()
