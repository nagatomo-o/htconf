#!/usr/bin/env python3
# coding:utf-8
import os
import sys
import re
import getopt
import shutil
import random
import string


def usage():
    """usage output
    """

    print('''
Usage: htconf [operation] [NAME] [options]              Read text from stdin and write to stdout
   or: htconf [operation] [NAME] [options] -f [file]    Edit file
   or: htconf --help                                    Usage output
Edit Apache configuration directives (stdin or file)

Arguments:
        operation     add,set,disable,enable
        NAME          directive name
                  (Add "<" ">" if section directive)
options:
        -v VALUE      Value of the directive to set
        -w VALUE      Matching Directive Value
        -s SECTION    Matching Directive Section
                  Format: <Section Name>:<Section Value>
''')


def abort(message):
    """Abort script
    :param message to print to stderr (optional)
    """
    print(f"[ERROR] {message}", file=sys.stderr) if message else None
    sys.exit(2)


def ok():
    """gracefully terminate the script
    """
    sys.exit(0)


def esc(string):
    """Escape strings for config values
    {string} string to escape
    """
    if ' ' in string or '"' in string or '\\' in string:
        return '"' + string.replace('\\', '\\\\') \
            .replace('"', '\\"') + '"'
    else:
        return string

def regexp(string):
    """Escape strings for regular expressions
    """
    return '"?' + string.replace('"', '\\"') \
            .replace('\\', '\\\\') \
            .replace('.', '\\.') \
            .replace('^', '\\^') \
            .replace('$', '\\$') \
            .replace('*', '\\*') \
            .replace('+', '\\+') \
            .replace('?', '\\?') \
            .replace('{', '\\{') \
            .replace('}', '\\}') \
            .replace('(', '\\(') \
            .replace(')', '\\)') \
            .replace('[', '\\[') \
            .replace(']', '\\]') \
            .replace('|', '\\|') + '"?'

def get_indent(string):
    """Get indent from string
    1: string
    """
    match = re.match(r'^( +)', string)
    if match:
        return match.group(1)
    else:
        return ''


def add_directive():
    """Add the directive at the end of file
    """
    global in_file, out_file
    global directive, values
    for line in in_file:
        print(line, end='', file=out_file)
    print(f"{directive}{values}", file=out_file)


def add_directive_with_section():
    """Add the directive at the end of spec section
    """
    global in_file, out_file
    global directive, values
    global section_name, section_value
    global section_start_pattern, section_end_pattern
    in_section = False
    indent = ""
    not_added = True
    for line in in_file:
        if re.match(section_start_pattern, line):
            in_section = True
            indent = get_indent(line)
            section_end_pattern = f"^{indent}</{section_name}>"

        if in_section and re.match(section_end_pattern, line):
            print(f"{indent}    {directive}{values}", file=out_file)
            in_section = False
            not_added = False
        print(line, end='', file=out_file)

    if not_added:
        print(f"<{section_name} {section_value}>", file=out_file)
        print(f"    {directive}{values}", file=out_file)
        print(f"</{section_name}>", file=out_file)


def set_directive():
    """Set the values of a directive
    """
    global in_file, out_file
    global directive, values
    global with_values
    directive_pattern = f"^ *{directive}{with_values}"
    for line in in_file:
        if re.match(directive_pattern, line):
            print(f"{ get_indent(line)}{directive}{values}", file=out_file)
        else:
            print(line, end='', file=out_file)


def set_directive_with_section():
    """Sets the value of a directive within the specified section
    """
    global in_file, out_file
    global directive, values
    global section_name, section_value
    global with_values
    global section_start_pattern, section_end_pattern
    directive_pattern = f"^ *{directive}{with_values}"
    in_section = False
    for line in in_file:
        if re.match(section_start_pattern, line):
            in_section = True
            section_end_pattern = f"^{get_indent(line)}</{section_name}>"

        if in_section and re.match(section_end_pattern, line):
            in_section = False

        if in_section and re.match(directive_pattern, line):
            print(f"{get_indent(line)}{directive}{values}", file=out_file)
        else:
            print(line, end='', file=out_file)


def set_section():
    """Set the directive values at the end
    """
    global in_file, out_file
    global directive, values
    global with_values
    directive_pattern = f"^ *<{directive}{with_values}"
    for line in in_file:
        if re.match(directive_pattern, line):
            print(f"{get_indent(line)}<{directive}{values}>", file=out_file)
        else:
            print(line, end='', file=out_file)


def set_section_with_section():
    """Set the directive values at the end
    """
    global in_file, out_file
    global directive, values
    global with_values
    global section_name, section_value
    global section_start_pattern, section_end_pattern
    directive_pattern = f"^ *<{directive}{with_values}"
    in_section = False
    for line in in_file:
        if re.match(section_start_pattern, line):
            in_section = True
            section_end_pattern = f"^{get_indent(line)}</{section_name}>"

        if in_section and re.match(section_end_pattern, line):
            in_section = False

        if in_section and re.match(directive_pattern, line):
            print(f"{get_indent(line)}<{directive}{values}>", file=out_file)
        print(line, end='', file=out_file)


def disable_directive():
    """Comment out the specified directive
    """
    global in_file, out_file
    global directive, values
    global with_values
    directive_pattern = f"^ *{directive}{with_values}"
    for line in in_file:
        if re.match(directive_pattern, line):
            print(re.sub(r'^( *)(.+)', r'\1#\2', line), end='', file=out_file)
        else:
            print(line, end='', file=out_file)


def disable_directive_with_section():
    """Comment out directives in the specified section
    """
    global in_file, out_file
    global directive, values
    global with_values
    global section_start_pattern, section_end_pattern
    directive_pattern = f"^ *{directive}{with_values}"
    in_section = False
    for line in in_file:
        if re.match(section_start_pattern, line):
            in_section = True
            section_end_pattern = f"^{get_indent(line)}</{section_name}>"

        if in_section and re.match(section_end_pattern, line):
            in_section = False

        if in_section and re.match(directive_pattern, line):
            print(re.sub(r'^( *)(.+)', r'\1#\2', line), end='', file=out_file)
        else:
            print(line, end='', file=out_file)


def enable_directive():
    """enable the specified directive
    """
    global in_file, out_file
    global directive, values
    global with_values
    directive_pattern = f"^ *#{directive}{with_values}"
    for line in in_file:
        if re.match(directive_pattern, line):
            print(re.sub(r'^( *)#(.+)', r'\1\2', line), end='', file=out_file)
        else:
            print(line, end='', file=out_file)


def enable_directive_with_section():
    """enable directives in the specified section
    """
    global in_file, out_file
    global directive, values
    global with_values
    global section_start_pattern, section_end_pattern
    directive_pattern = f"^ *#{directive}{with_values}"
    in_section = False
    for line in in_file:
        if re.match(section_start_pattern, line):
            in_section = True
            section_end_pattern = f"^{get_indent(line)}</{section_name}>"

        if in_section and re.match(section_end_pattern, line):
            in_section = False

        if in_section and re.match(directive_pattern, line):
            print(re.sub(r'^( *)#(.+)', r'\1\2', line), end='', file=out_file)
        else:
            print(line, end='', file=out_file)


##
# Main
##
# print usage if no argument or help argument
if len(sys.argv) == 0:
    usage()
    ok()

if len(sys.argv) == 1 and sys.argv[1] == "help" or sys.argv[1] == "--help":
    usage()
    ok()

if len(sys.argv) < 2:
    usage()
    ok()

in_file = None
out_file = None
operation = sys.argv[1]
directive = sys.argv[2]
values = ""
with_values = ""
with_section = ""
section_name = ""
section_value = ""
section_start_pattern = ""
section_end_pattern = ""
file_path = ""

# print usage if no argument or help argument
if len(sys.argv) == 0 or sys.argv[0] == "help" or sys.argv[0] == "--help":
    usage()
    ok()

# Assign option value to variable
operation = sys.argv[1]
directive = sys.argv[2]
in_file = sys.stdin
out_file = sys.stdout
short_options = "v:w:s:f:"
long_options = ["value=", "with=", "section=", "file="]
options, _ = getopt.getopt(sys.argv[3:], short_options, long_options)
for opt, optarg in options:
    if opt in ("-v", "--value"):
        values += " " + esc(optarg)
    elif opt in ("-w", "--with"):
        with_values += " +" + regexp(optarg)
    elif opt in ("-s", "--section"):
        with_section = optarg
    elif opt in ("-f", "--file"):
        file_path = optarg

# Create a section regular expression from the with_section variable
if with_section:
    if ':' in with_section:
        section_name, section_value = with_section.split(":")
        section_start_pattern = f"^( *)<({section_name}) +({regexp(section_value)})"
    else:
        section_name = with_section
        section_start_pattern = f"^ *<{section_name} .+>"

# Construct the name of the function to execute
func = operation
match = re.match(r'^\<(.+)\>', directive)
if match:
    directive = match.group(1)
    func += "_section"
else:
    func += "_directive"

if with_section:
    func += "_with_section"

# Rewrite the file if there is an file_path variable
if file_path:
    letters = string.ascii_letters + string.digits
    tmp_file = ''.join(random.choice(letters) for _ in range(16))
    shutil.copyfile(file_path, tmp_file)
    with open(tmp_file, 'r') as in_file, open(file_path, 'w') as out_file:
        eval(func + "()")
    os.remove(tmp_file)
    ok
else:
    # Piping if there is no file_path variable
    in_file = sys.stdin
    out_file = sys.stdout
    eval(func + "()")
    ok
