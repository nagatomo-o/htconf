#!/usr/bin/env python3
# coding:utf-8
import sys
import io
import re
import getopt
import shlex


def usage(output=sys.stdout):
    """usage output"""
    print('''
Usage: htconf [operation] [NAME] [options]              Edit text as pipe
   or: htconf [operation] [NAME] [options] -f [file]    Edit text file
   or: htconf -e "[ARGS]" -e "[ARGS]" ...               Edit text with multiple operations as a pipe
   or: htconf -e "[ARGS]" -e "[ARGS]" ... -f [file]     Edit text file with multiple operations
   or: htconf --help                                    Show usage information
Edit Apache configuration directives (stdin or file)

Arguments:
        operation     add, set, disable, enable
        NAME          Directive name
                      If it is a section directive name, enclose it with "<" and ">"
Options:
        -v VALUE      Value of the directive to set
        -w VALUE      Matching Directive Value
        -s SECTION    Matching Directive Section
                      Format: <Section Name>:<Section Value>
        -f FILE       Editing file
        -e ARGS       [operation] [NAME] [options] as string
''', file=output)


def esc_conf(string: str) -> str:
    """Escape strings for config values"""
    if ' ' in string or '"' in string or '\\' in string:
        return '"' + string.replace('\\', '\\\\').replace('"', '\\"') + '"'
    else:
        return string


def esc_regexp(string: str) -> str:
    """Escape strings for regular expressions"""
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


def get_indent(string: str) -> str:
    """Get indent from string"""
    return string[:len(string) - len(string.lstrip())]


class Editor:
    operation: str = ''
    directive: str = ''
    values: str = ''
    with_values: str = ''
    with_section: str = ''
    section_name: str = ''
    section_value: str = ''
    section_start_pattern: str = ''
    file_path: str = ''

    def __init__(self, argv):
        self.operation = argv[1]
        self.directive = argv[2]
        # Assign option value to variable
        options, _ = getopt.getopt(argv[3:], 'v:w:s:f:',
                                   ['value=', 'with=', 'section=', 'file='])
        for opt, optarg in options:
            if opt in ('-v', '--value'):
                self.values += ' ' + esc_conf(optarg)
            elif opt in ('-w', '--with'):
                self.with_values += ' +' + esc_regexp(optarg)
            elif opt in ('-s', '--section'):
                self.with_section = optarg
            elif opt in ('-f', '--file'):
                self.file_path = optarg

        # Create a section regular expression from the with_section variable
        if self.with_section:
            if ':' in self.with_section:
                self.section_name, self.section_value = self.with_section.split(
                    ':')
                self.section_start_pattern = f"^( *)<({self.section_name}) +({esc_regexp(self.section_value)})"
            else:
                self.section_name = self.with_section
                self.section_start_pattern = f"^ *<{self.section_name} .+>"

        # Construct the name of the function to execute
        if not self.operation in ('add', 'set', 'enable', 'disable'):
            print(f"Unknown Operation ({self.operation})", file=sys.stderr)
            sys.exit(1)
        self.func = self.operation
        match = re.match(r'<(\w+)>', self.directive)
        if match:
            if self.operation != "set":
                print(f"Unsupported Operation ({self.operation} {self.directive})",
                      file=sys.stderr)
                sys.exit(1)

            self.directive = match.group(1)
            self.func += '_section'
        else:
            self.func += '_directive'

        if self.with_section:
            self.func += '_with_section'

    def add_directive(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Add the directive at the end of file"""
        for line in instream:
            print(line, end='', file=outstream)
        print(f"{self.directive}{self.values}", file=outstream)

    def add_directive_with_section(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Add the directive at the end of the section"""
        in_section = False
        indent = ''
        not_added = True
        for line in instream:
            if re.match(self.section_start_pattern, line):
                in_section = True
                indent = get_indent(line)
                section_end_pattern = f"^{indent}</{self.section_name}>"

            if in_section and re.match(section_end_pattern, line):
                print(f"{indent}    {self.directive}{self.values}",
                      file=outstream)
                in_section = False
                not_added = False
            print(line, end='', file=outstream)

        if not_added:
            print(f"<{self.section_name} {self.section_value}>", file=outstream)
            print(f"    {self.directive}{self.values}", file=outstream)
            print(f"</{self.section_name}>", file=outstream)

    def set_directive(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Set the values of the directive"""
        directive_pattern = f"^ *{self.directive}{self.with_values}"
        for line in instream:
            if re.match(directive_pattern, line):
                print(f"{ get_indent(line)}{self.directive}{self.values}",
                      file=outstream)
            else:
                print(line, end='', file=outstream)

    def set_directive_with_section(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Set the values of the directive within the section"""
        directive_pattern = f"^ *{self.directive}{self.with_values}"
        in_section = False
        for line in instream:
            if re.match(self.section_start_pattern, line):
                in_section = True
                section_end_pattern = f"^{get_indent(line)}</{self.section_name}>"

            if in_section and re.match(section_end_pattern, line):
                in_section = False

            if in_section and re.match(directive_pattern, line):
                print(f"{get_indent(line)}{self.directive}{self.values}",
                      file=outstream)
            else:
                print(line, end='', file=outstream)

    def set_section(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Set the values of the section directive"""
        directive_pattern = f"^ *<{self.directive}{self.with_values}"
        for line in instream:
            if re.match(directive_pattern, line):
                print(f"{get_indent(line)}<{self.directive}{self.values}>",
                      file=outstream)
            else:
                print(line, end='', file=outstream)

    def set_section_with_section(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Set the values of the section directive within the section"""
        directive_pattern = f"^ *<{self.directive}{self.with_values}"
        in_section = False
        for line in instream:
            if re.match(self.section_start_pattern, line):
                in_section = True
                section_end_pattern = f"^{get_indent(line)}</{self.section_name}>"

            if in_section and re.match(section_end_pattern, line):
                in_section = False

            if in_section and re.match(directive_pattern, line):
                print(f"{get_indent(line)}<{self.directive}{self.values}>",
                      file=outstream)
            else:
                print(line, end='', file=outstream)

    def disable_directive(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Comment out the directive"""
        directive_pattern = f"^ *{self.directive}{self.with_values}"
        for line in instream:
            if re.match(directive_pattern, line):
                print(re.sub(r'^( *)(.+)', r'\1#\2', line),
                      end='', file=outstream)
            else:
                print(line, end='', file=outstream)

    def disable_directive_with_section(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Comment out the directive inside the section"""
        directive_pattern = f"^ *{self.directive}{self.with_values}"
        in_section = False
        for line in instream:
            if re.match(self.section_start_pattern, line):
                in_section = True
                section_end_pattern = f"^{get_indent(line)}</{self.section_name}>"

            if in_section and re.match(section_end_pattern, line):
                in_section = False

            if in_section and re.match(directive_pattern, line):
                print(re.sub(r'^( *)(.+)', r'\1#\2', line),
                      end='', file=outstream)
            else:
                print(line, end='', file=outstream)

    def enable_directive(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Enable the directive and set its values"""
        directive_pattern = f"^ *#{self.directive}{self.with_values}"
        for line in instream:
            if re.match(directive_pattern, line):
                if self.values:
                    print(f"{ get_indent(line)}{self.directive}{self.values}",
                          file=outstream)
                else:
                    print(re.sub(r'^( *)#(.+)', r'\1\2', line),
                          end='', file=outstream)
            else:
                print(line, end='', file=outstream)

    def enable_directive_with_section(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        """Enables the directive within the section and set its values"""
        directive_pattern = f"^ *#{self.directive}{self.with_values}"
        in_section = False
        for line in instream:
            if re.match(self.section_start_pattern, line):
                in_section = True
                section_end_pattern = f"^{get_indent(line)}</{self.section_name}>"

            if in_section and re.match(section_end_pattern, line):
                in_section = False

            if in_section and re.match(directive_pattern, line):
                if self.values:
                    print(f"{ get_indent(line)}{self.directive}{self.values}",
                          file=outstream)
                else:
                    print(re.sub(r'^( *)#(.+)', r'\1\2', line),
                          end='', file=outstream)
            else:
                print(line, end='', file=outstream)

    def edit(self):
        if self.file_path:
            self.edit_file(self.file_path)
        else:
            self.edit_stream(sys.stdin, sys.stdout)

    def edit_file(self, file_path):
        with open(file_path, 'r') as read_file:
            conf = read_file.read()
        with open(file_path, 'w') as outstream:
            self.edit_stream(io.StringIO(conf), outstream)

    def edit_text(self, conf: str) -> str:
        with io.StringIO() as outstream:
            self.edit_stream(io.StringIO(conf), outstream)
            return outstream.getvalue()

    def edit_stream(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        eval(f"self.{self.func}")(instream, outstream)


class Expressions:
    editors = []

    def add(self, editor: Editor):
        self.editors.append(editor)

    def edit_file(self, file_path: str):
        text = ''
        with open(file_path, 'r') as instream:
            text = instream.read()
        for editor in self.editors:
            text = editor.edit_text(text)
        with open(file_path, 'w') as outstream:
            outstream.write(text)

    def edit_stream(self, instream: io.TextIOWrapper, outstream: io.TextIOWrapper):
        text = instream.read()
        for editor in self.editors:
            text = editor.edit_text(text)
        outstream.write(text)


##
# Main
##
if __name__ == '__main__':
    # print usage if no argument or help argument
    if len(sys.argv) == 1:
        usage(sys.stderr)
    elif len(sys.argv) == 2 and sys.argv[1] in ('help', '--help'):
        usage()
    elif len(sys.argv) > 2 and '-e' in sys.argv:
        expressions = Expressions()
        file_path = ''
        options, _ = getopt.getopt(sys.argv[1:], 'e:f:',
                                   ['expression=', 'file='])
        for opt, optarg in options:
            if opt in ('-e', '--expression'):
                expressions.add(Editor([__file__] + shlex.split(optarg)))
            elif opt in ('-f', '--file'):
                file_path = optarg
        if file_path:
            expressions.edit_file(file_path)
        else:
            expressions.edit_stream(sys.stdin, sys.stdout)

    elif len(sys.argv) > 2:
        editor = Editor(sys.argv)
        editor.edit()
