#!/bin/bash
source ./htconf.sh
# Tests for the esc_conf() function
test_esc_no_escape() {
  actual=$(esc_conf "hello")
  expect="hello"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_conf_space() {
  actual=$(esc_conf "hello world")
  expect="\"hello world\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_conf_quote() {
  actual=$(esc_conf "hello\"world")
  expect="\"hello\\\"world\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_conf_backslash() {
  actual=$(esc_conf "hello\\world")
  expect="\"hello\\\\world\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_conf_multiple_chars() {
  actual=$(esc_conf "he\"llo\\w\"orl\\\"d")
  expect="\"he\\\"llo\\\\w\\\"orl\\\\\\\"d\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

# Tests for the esc_regexp() function
test_esc_regexp_no_escape(){
  actual=$(esc_regexp "hello world")
  expect="\"?hello world\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_dot(){
  actual=$(esc_regexp "hello.worl.d")
  expect="\"?hello\\.worl\\.d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_backslash(){
  actual=$(esc_regexp "hello\\worl\\d")
  expect="\"?hello\\\\worl\\\\d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_aster(){
  actual=$(esc_regexp "hello*worl*d")
  expect="\"?hello\\*worl\\*d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_plus(){
  actual=$(esc_regexp "hello+worl+d")
  expect="\"?hello\\+worl\\+d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_question(){
  actual=$(esc_regexp "hello?worl?d")
  expect="\"?hello\\?worl\\?d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_brackets(){
  actual=$(esc_regexp "[hello[ ]world]")
  expect="\"?\\[hello\\[ \\]world\\]\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_parentheses(){
  actual=$(esc_regexp "(hello( )world)")
  expect="\"?\\(hello\\( \\)world\\)\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_braces(){
  actual=$(esc_regexp "{hello{ }world}")
  expect="\"?\\{hello\\{ \\}world\\}\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_doll(){
  actual=$(esc_regexp "hello\$worl\$d")
  expect="\"?hello\\\$worl\\\$d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_tilde(){
  actual=$(esc_regexp "hello^worl^d")
  expect="\"?hello\\^worl\\^d\"?"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_esc_regexp_verticalbar(){
  actual=$(esc_regexp "hello|worl|d")
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
source ./shunit2/shunit2
