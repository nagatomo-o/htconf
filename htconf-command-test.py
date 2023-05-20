#!/usr/bin/env python3
# coding:utf-8
import os
import subprocess
import unittest
import tempfile

HTCONF = os.path.join(os.getcwd(), "htconf.py")
SAMPLE = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""


def run(args, input):
    res = subprocess.run(["python", HTCONF] + args,
                         input=input, text=True, capture_output=True)
    if res.returncode != 0:
        raise Exception(res.stderr)
    return res.stdout


def call(args):
    returncode = subprocess.call(["python", HTCONF] + args)
    if returncode != 0:
        print(["python", HTCONF] + args)
        raise Exception()


class TestAddDirective(unittest.TestCase):
    def test_add_directive_single_value_without_section(self):
        actual = run(["add", "Dir9", "-v", "AAA"], SAMPLE)
        expect = SAMPLE + "Dir9 AAA\n"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_add_directive_multi_value_without_section(self):
        actual = run(["add", "Dir9", "-v", "BBB", "-v",
                      "{\"name\":\"value\"}"], SAMPLE)
        expect = SAMPLE + "Dir9 BBB \"{\\\"name\\\":\\\"value\\\"}\"\n"
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_add_directive_multi_value_with_noexists_section(self):
        actual = run(["add", "Dir9", "-v", "CCC", "-v",
                      "{\"path\":\"c:\\path\"}", "-s", "Sec3:DDD"], SAMPLE)
        expect = SAMPLE + """<Sec3 DDD>
    Dir9 CCC \"{\\\"path\\\":\\\"c:\\\\path\\\"}\"
</Sec3>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_add_directive_multi_value_with_first_section(self):
        actual = run(["add", "Dir9", "-v", "EEE", "-v",
                      "/a[ ]+$/", "-s", "Sec1:/"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
    Dir9 EEE \"/a[ ]+$/\"
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_add_directive_multi_value_with_second_section(self):
        actual = run(["add", "Dir9", "-v", "FFF", "-v",
                      "/a[ ]+$/", "-s", "Sec2:/var/www"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
        Dir9 FFF \"/a[ ]+$/\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")


class TestSetDirective(unittest.TestCase):
    def test_set_directive_single_value_without_value_without_section(self):
        actual = run(["set", "Dir2", "-v", "Off"], SAMPLE)
        expect = """Dir1 None
Dir2 Off
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 Off
    Dir2 Off
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_set_directive_multi_value_without_value_without_section(self):
        actual = run(["set", "Dir4", "-v", "On", "-v",
                      "{\"name\":\"value\"}"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    <Sec2 \"/var/www\">
        Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_set_directive_multi_value_with_single_value_without_section(self):
        actual = run(["set", "Dir4", "-v", "Off", "-v",
                      "{\"name\":\"value\"}", "-w", "On"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 Off \"{\\\"name\\\":\\\"value\\\"}\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_set_directive_multi_value_with_multi_value_without_section(self):
        actual = run(["set", "Dir4", "-v", "On", "-v",
                      "{\"name\":\"value\"}", "-w", "Off", "-w", "($)+"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_set_directive_multi_value_with_multi_value_with_section(self):
        actual = run(["set", "Dir4", "-v", "On", "-v",
                      "{\"name\":\"value\"}", "-w", "Off", "-w", "[*].?", "-s", "Sec2:/var/www"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 On \"{\\\"name\\\":\\\"value\\\"}\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_set_section_single_value_with_single_value_without_section(self):
        actual = run(
            ["set", "<Sec1>", "-v", "{\"name\":\"value\"}", "-w", "/"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 \"{\\\"name\\\":\\\"value\\\"}\">
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_set_section_single_value_with_single_value_with_section(self):
        actual = run(["set", "<Sec2>", "-v", "/var/www/html",
                      "-w", "/var/www", "-s", "Sec1:/"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 /var/www/html>
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_set_section_single_value_with_single_value_with_section_fole(self):
        actual_file = os.path.join(tempfile.gettempdir(), "httpd.conf")
        with open(actual_file, 'w') as f:
            f.write(SAMPLE)

        call(["set", "<Sec2>", "-v", "/var/www/html",
             "-w", "/var/www", "-s", "Sec1:/", "-f", actual_file])
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 /var/www/html>
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        with open(actual_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expect, actual, "Result should match expected output")


class TestDisableDirective(unittest.TestCase):
    def test_disable_directive_without_value_without_section(self):
        actual = run(["disable", "Dir2"], SAMPLE)
        expect = """Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_disable_directive_with_single_value_without_section(self):
        actual = run(["disable", "Dir2", "-w", "None"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_disable_directive_with_multi_value_without_section(self):
        actual = run(["disable", "Dir4", "-w", "Off", "-w", "($)+"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    #Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_disable_directive_with_multi_value_with_section(self):
        actual = run(["disable", "Dir4", "-w", "Off", "-w",
                      "[*].?", "-s", "Sec2:/var/www"], SAMPLE)
        expect = """Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
Dir3 On \"($)+\"
Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")


SAMPLE2 = """#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"($)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"($)+\"
    #Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""


class TestEnableDirective(unittest.TestCase):
    def test_enable_directive_without_value_without_section(self):
        actual = run(["enable", "Dir2"], SAMPLE2)
        expect = """#Dir1 None
Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"($)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"($)+\"
    #Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_disable_directive_with_single_value_without_section(self):
        actual = run(["enable", "Dir2", "-w", "None"], SAMPLE2)
        expect = """#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"($)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"($)+\"
    #Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_enable_directive_with_multi_value_without_section(self):
        actual = run(["enable", "Dir4", "-w", "Off", "-w", "($)+"], SAMPLE2)
        expect = """#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"($)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"($)+\"
    Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        #Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")

    def test_enable_directive_with_multi_value_with_section(self):
        actual = run(["enable", "Dir4", "-w", "Off", "-w",
                      "[*].?", "-s", "Sec2:/var/www"], SAMPLE2)
        expect = """#Dir1 None
#Dir2 \"\\\"a\\\\z\\\"\"
#Dir3 On \"($)+\"
#Dir4 Off \"[*].?\"
<Sec1 />
    #Dir2 None
    #Dir2 \"\\\"a\\\\z\\\"\"
    #Dir4 On \"($)+\"
    #Dir4 Off \"($)+\"
    <Sec2 \"/var/www\">
        Dir4 Off \"[*].?\"
    </Sec2>
</Sec1>
"""
        self.assertEqual(expect, actual, "Result should match expected output")


if __name__ == '__main__':
    unittest.main()
