#!/bin/bash

HTCONF="./htconf.sh"
SAMPLE="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"

# add directive
test_add_directive_single_value_without_section() {
  actual=$(echo "$SAMPLE" | $HTCONF add Dir9 -v AAA)
  expect="$SAMPLE
Dir9 AAA"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_add_directive_multi_value_without_section() {
  actual=$(echo "$SAMPLE" | $HTCONF add Dir9 -v BBB -v "{\"name\":\"value\"}")
  expect="$SAMPLE
Dir9 BBB \"{\\\"name\\\":\\\"value\\\"}\""
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_add_directive_multi_value_with_noexists_section() {
  actual=$(echo "$SAMPLE" | $HTCONF add Dir9 -v CCC -v "{\"path\":\"c:\\path\"}" -s Sec3:DDD)
  expect="$SAMPLE
<Sec3 DDD>
    Dir9 CCC \"{\\\"path\\\":\\\"c:\\\\path\\\"}\"
</Sec3>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_add_directive_multi_value_with_first_section() {
  actual=$(echo "$SAMPLE" | $HTCONF add Dir9 -v EEE -v "/a[ ]+\$/" -s Sec1:/)
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
    Dir9 EEE \"/a[ ]+\$/\"
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_add_directive_multi_value_with_second_section() {
  actual=$(echo "$SAMPLE" | $HTCONF add Dir9 -v FFF -v "/a[ ]+\$/" -s "Sec2:/var/www")
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
        Dir9 FFF \"/a[ ]+\$/\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

# set directive
test_set_directive_single_value_without_value_without_section() {
  actual=$(echo "$SAMPLE" | $HTCONF set Dir2 -v Off)
  expect="Dir1 None
Dir2 Off
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 Off
    Dir2 Off
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_set_directive_multi_value_without_value_without_section() {
  actual=$(echo "$SAMPLE" | $HTCONF set Dir4 -v On -v "{\"name\":\"value\"}")
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    <Sec2 \"/var/www\">
        Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_set_directive_multi_value_with_single_value_without_section() {
  actual=$(echo "$SAMPLE" | $HTCONF set Dir4 -v Off -v "{\"name\":\"value\"}" -w On)
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 Off \"{\\\"name\\\":\\\"value\\\"}\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_set_directive_multi_value_with_multi_value_without_section() {
  actual=$(echo "$SAMPLE" | $HTCONF set Dir4 -v On -v "{\"name\":\"value\"}" -w Off -w "(\$)+")
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_set_directive_multi_value_with_multi_value_with_section(){
  actual=$(echo "$SAMPLE" | $HTCONF set Dir4 -v On -v "{\"name\":\"value\"}" -w Off -w "[*].?" -s Sec2:/var/www)
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_set_section_single_value_with_single_value_without_section(){
  actual=$(echo "$SAMPLE" | $HTCONF set "<Sec1>" -v "{\"name\":\"value\"}" -w /)
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 \"{\\\"name\\\":\\\"value\\\"}\">
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_set_section_single_value_with_single_value_with_section(){
  actual=$(echo "$SAMPLE" | $HTCONF set "<Sec2>" -v "/var/www/html" -w /var/www -s Sec1:/)
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 /var/www/html>
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_set_section_single_value_with_single_value_with_section_file() {
  actual_file=/tmp/httpd.conf
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 /var/www/html>
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  echo "$SAMPLE" > $actual_file
  $HTCONF set "<Sec2>" -v "/var/www/html" -w /var/www -s Sec1:/ -f $actual_file
  actual=$(cat $actual_file)
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_disable_directive_without_value_without_section(){
  actual=$(echo "$SAMPLE" | $HTCONF disable Dir2)
  expect="Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_disable_directive_with_single_value_without_section(){
  actual=$(echo "$SAMPLE" | $HTCONF disable Dir2 -w None)
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_disable_directive_with_multi_value_without_section(){
  actual=$(echo "$SAMPLE" | $HTCONF disable Dir4 -w Off -w "(\$)+")
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    #Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_disable_directive_with_multi_value_with_section(){
  actual=$(echo "$SAMPLE" | $HTCONF disable Dir4 -w Off -w "[*].?" -s Sec2:/var/www)
  expect="Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"(\$)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

SAMPLE2="#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"(\$)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"(\$)+\"
    #Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"

test_enable_directive_without_value_without_section(){
  actual=$(echo "$SAMPLE2" | $HTCONF enable Dir2)
  expect="#Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"(\$)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"(\$)+\"
    #Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_enable_directive_with_single_value_without_section(){
  actual=$(echo "$SAMPLE2" | $HTCONF enable Dir2 -w None)
  expect="#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"(\$)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"(\$)+\"
    #Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_enable_directive_with_multi_value_without_section(){
  actual=$(echo "$SAMPLE2" | $HTCONF enable Dir4 -w Off -w "(\$)+")
  expect="#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"(\$)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"(\$)+\"
    Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

test_enable_directive_with_multi_value_with_section(){
  actual=$(echo "$SAMPLE2" | $HTCONF enable Dir4 -w Off -w "[*].?" -s Sec2:/var/www)
  expect="#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"(\$)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"(\$)+\"
    #Dir4 Off \"(\$)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>"
  assertEquals "Result should match expected output" "$expect" "$actual"
}

# Load and run shUnit2.
source ./shunit2/shunit2
