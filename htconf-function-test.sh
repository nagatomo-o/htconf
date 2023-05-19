#!/bin/bash
source ./htconf.sh
# Tests for the esc() function
test_esc_no_escape() {
  actual=$(esc "hello")
  expect="hello"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_escape_space() {
  actual=$(esc "hello world")
  expect="\"hello world\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_escape_quote() {
  actual=$(esc "hello\"world")
  expect="\"hello\\\"world\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_escape_backslash() {
  actual=$(esc "hello\\world")
  expect="\"hello\\\\world\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_escape_multiple_chars() {
  actual=$(esc "he\"llo\\w\"orl\\\"d")
  expect="\"he\\\"llo\\\\w\\\"orl\\\\\\\"d\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

# Tests for the regexp() function
test_regexp_no_escape(){
  actual=$(regexp "hello world")
  expect="\"?hello world\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_dot(){
  actual=$(regexp "hello.worl.d")
  expect="\"?hello\\.worl\\.d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_backslash(){
  actual=$(regexp "hello\\worl\\d")
  expect="\"?hello\\\\worl\\\\d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_aster(){
  actual=$(regexp "hello*worl*d")
  expect="\"?hello\\*worl\\*d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_plus(){
  actual=$(regexp "hello+worl+d")
  expect="\"?hello\\+worl\\+d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_question(){
  actual=$(regexp "hello?worl?d")
  expect="\"?hello\\?worl\\?d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_brackets(){
  actual=$(regexp "[hello[ ]world]")
  expect="\"?\\[hello\\[ \\]world\\]\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_parentheses(){
  actual=$(regexp "(hello( )world)")
  expect="\"?\\(hello\\( \\)world\\)\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_braces(){
  actual=$(regexp "{hello{ }world}")
  expect="\"?\\{hello\\{ \\}world\\}\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_doll(){
  actual=$(regexp "hello\$worl\$d")
  expect="\"?hello\\\$worl\\\$d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_tilde(){
  actual=$(regexp "hello^worl^d")
  expect="\"?hello\\^worl\\^d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_regexp_verticalbar(){
  actual=$(regexp "hello|worl|d")
  expect="\"?hello\\|worl\\|d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

# Tests for the get_indent() function
test_get_indent_space(){
  actual=$(get_indent '   This is indented')
  expect='   '
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_get_indent_tab(){
  actual=$(get_indent '		This is indented with tabs')
  expect='		'
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_get_indent_none(){
  actual=$(get_indent 'No indentation here.')
  expect=''
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_get_indent_mixed(){
  actual=$(get_indent '    	Some spaces, but also tabs')
  expect='    	'
  assertEquals "Result should match expected output" "$expect" "$actual"
}

# Load and run shUnit2.
source ./shunit2-2.1.8/shunit2
