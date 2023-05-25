#!/bin/bash -eu
##
# usage output
##
usage(){
  cat <<EOF
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
EOF
}

##
# Escape strings for config values
# $1: string to escape
##
esc_conf() {
  local re='[ "\\]'
  if [[ $1 =~ $re ]]; then
    echo "$1" | sed \
      -e 's/\\/\\\\/g' \
      -e 's/"/\\"/g' \
      -e 's/^/"/' \
      -e 's/$/"/'
  else
    echo "$1"
  fi
}

##
# Escape strings for regular expressions
# $1: string to escape
##
esc_regexp() {
  echo "$1" | sed \
    -e 's/"/\\"/g' \
    -e 's/\\/\\\\/g' \
    -e 's/\./\\./g' \
    -e 's/\^/\\^/g' \
    -e 's/\$/\\$/g' \
    -e 's/*/\\*/g' \
    -e 's/+/\\+/g' \
    -e 's/?/\\?/g' \
    -e 's/{/\\{/g' \
    -e 's/}/\\}/g' \
    -e 's/(/\\(/g' \
    -e 's/)/\\)/g' \
    -e 's/\[/\\[/g' \
    -e 's/\]/\\]/g' \
    -e 's/|/\\|/g' \
    -e 's/^/"?/' \
    -e 's/$/"?/'
}

##
# Get indent from string
##
get_indent(){
  echo "$1" | sed -E -e 's/^([ \t]*).+$/\1/'
}

##
# Add the directive at the end of file
##
add_directive() {
  while IFS= read -r line; do
    echo "$line"
  done
  echo "$directive$values"
}

##
# Add the directive at the end of the section
##
add_directive_with_section() {
  local in_section=false
  local indent=""
  local not_added=true
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $section_start_pattern ]]; then
      in_section=true
      indent=$(get_indent "$line")
      section_end_pattern="^$indent</$section_name>"
    fi

    if $in_section && [[ $line =~ $section_end_pattern ]]; then
      echo "$indent    $directive$values"
      in_section=false
      not_added=false
    fi
    echo "$line"
  done

  if $not_added; then
    echo "<$section_name `esc_conf "$section_value"`>"
    echo "    $directive$values"
    echo "</$section_name>"
  fi
}

##
# Set the values of the directive
##
set_directive() {
  directive_pattern="^ *$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $directive_pattern ]]; then
      echo "`get_indent "$line"`$directive$values"
    else
      echo "$line"
    fi
  done
}

##
# Set the values of the directive within the section
##
set_directive_with_section() {
  directive_pattern="^ *$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^`get_indent "$line"`</$section_name>"
    fi

    if $in_section && [[ $line =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ $line =~ $directive_pattern ]]; then
      echo "`get_indent "$line"`$directive$values"
    else
      echo "$line"
    fi
  done
}

##
# Set the values of the section directive
##
set_section() {
  directive=$(echo "$directive" | sed -E -e 's/^<(.+)>$/\1/')
  directive_pattern="^ *<$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $directive_pattern ]]; then
      echo "`get_indent "$line"`<$directive$values>"
    else
      echo "$line"
    fi
  done
}

##
# Set the values of the section directive within the section
##
set_section_with_section() {
  directive=$(echo "$directive" | sed -E -e 's/^<(.+)>$/\1/')
  directive_pattern="^ *<$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^`get_indent "$line"`</$section_name>"
    fi

    if $in_section && [[ $line =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ $line =~ $directive_pattern ]]; then
      echo "`get_indent "$line"`<$directive$values>"
    else
      echo "$line"
    fi
  done
}

##
# Comment out the directive
##
disable_directive() {
  directive_pattern="^ *$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $directive_pattern ]]; then
      echo "$line" | sed -E -e 's/^( *)(.+)$/\1#\2/'
    else
      echo "$line"
    fi
  done
}
##
# Comment out the directive inside the section
##
disable_directive_with_section() {
  directive_pattern="^ *$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^`get_indent "$line"`</$section_name>"
    fi

    if $in_section && [[ $line =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ $line =~ $directive_pattern ]]; then
      echo "$line" | sed -E -e 's/^( *)(.+)$/\1#\2/'
    else
      echo "$line"
    fi
  done
}

##
# Enable the directive and set its values
##
enable_directive() {
  directive_pattern="^ *#$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $directive_pattern ]]; then
      if [ -n "$values" ]; then
        echo "`get_indent "$line"`$directive$values"
      else
        echo "$line" | sed -E -e 's/^( *)#(.+)$/\1\2/'
      fi
    else
      echo "$line"
    fi
  done
}

##
# Enables the directive within the section and set its values
##
enable_directive_with_section() {
  directive_pattern="^ *#$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ $line =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^`get_indent "$line"`</$section_name>"
    fi

    if $in_section && [[ $line =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ $line =~ $directive_pattern ]]; then
      if [ -n "$values" ]; then
        echo "`get_indent "$line"`$directive$values"
      else
        echo "$line" | sed -E -e 's/^( *)#(.+)$/\1\2/'
      fi
    else
      echo "$line"
    fi
  done
}

##
# Main
##
operation=""
directive=""
directive_pattern=""
values=""
with_values=""
with_section=""
section_name=""
section_value=""
section_start_pattern=""
section_end_pattern=""
file_path=""
if [ $# -eq 0 ]; then
  usage >&2
elif [ $# -eq 1 ] && [ "$1" = 'help' -o "$1" = '--help' ]; then
  usage
elif [ $# -gt 1 ] && [[ $@ = *"-e "* ]]; then
  pipes=""
  while getopts e:f: OPT; do
    case $OPT in
      e) pipes+=" | $0 $OPTARG";;
      f) file_path="$OPTARG";;
    esac
  done
  if [ -n "$file_path" ]; then
    tmp_file="/tmp/htconf-${RANDOM}.conf"
    exec sh -s << EOF
cp "$file_path" $tmp_file
cat $tmp_file $pipes > "$file_path"
rm -f $tmp_file
EOF
  else
    exec sh -c "cat - $pipes"
  fi
elif [ $# -gt 1 ]; then
  operation="$1"
  directive="$2"
  # Assign option value to variable
  shift 2
  while getopts v:w:s:f: OPT; do
    case $OPT in
      v) values+=" `esc_conf "$OPTARG"`";;
      w) with_values+=" +`esc_regexp "$OPTARG"`";;
      s) with_section="$OPTARG";;
      f) file_path="$OPTARG";;
    esac
  done
  # Create a section regular expression from the with_section variable
  if [ -n "$with_section" ]; then
    if [[ $with_section = *":"* ]]; then
      section_name=$(echo "$with_section" | cut -d ':' -f 1)
      section_value=$(echo "$with_section" | cut -d ':' -f 2)
      section_start_pattern="^ *<$section_name +`esc_regexp "$section_value"`"
    else
      section_name="$with_section"
      section_start_pattern="^ *<$section_name "
    fi
  fi
  # Construct the name of the function to execute
  if [[ ! $operation =~ ^(add|set|enable|disable)$ ]]; then
    echo "Unknown Operation ($operation)" >&2
    exit 1
  fi
  func="$operation"
  if [[ $directive =~ ^\<[0-9A-Za-z_]+\>$ ]]; then
    if [ "$operation" != "set" ]; then
      echo "Unsupported Operation ($operation $directive)" >&2
      exit 1
    fi
    func+="_section"
  else
    func+="_directive"
  fi
  if [ -n "$with_section" ]; then
    func+="_with_section"
  fi
  oldifs="$IFS"
  # Rewrite the file if there is an file_path variable
  if [ -n "$file_path" ]; then
    tmp_file="/tmp/htconf-${RANDOM}.conf"
    cp "$file_path" $tmp_file
    cat $tmp_file | $func > "$file_path"
    rm -f $tmp_file
  else
    # Piping if there is no file_path variable
    $func
  fi
  IFS="$oldifs"
fi
