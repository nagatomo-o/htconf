#!/bin/bash -eu
##
# usage output
##

##
# usage output
##
usage(){
  cat <<EOF
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
EOF
}

##
# Abort script
# $1: message to print to stderr (optional)
##
abort(){
  test -n "$1" && echo "[ERROR] $1" >&2
  IFS="$oldifs"
  exit 2
}

##
# gracefully terminate the script
##
ok(){
  IFS="$oldifs"
  exit 0
}

##
# Escape strings for config values
# $1: string to escape
##
esc() {
  if [[ "$1" = *" "* ]] || [[ "$1" = *"\""* ]] || [[ "$1" = *"\\"* ]]; then
    echo "$1" \
    | sed -e 's/\\/\\\\/g' \
    | sed -e 's/"/\\\\"/g' \
    | sed -e 's/^/"/' \
    | sed -e 's/$/"/'
  else
    echo "$1"
  fi
}

##
# Escape strings for regular expressions
# $1: string to escape
##
regexp() {
  echo "$1" \
    | sed -e 's/"/\\"/g' \
    | sed -e 's/\\/\\\\/g' \
    | sed -e 's/\./\\./g' \
    | sed -e 's/\^/\\^/g' \
    | sed -e 's/\$/\\$/g' \
    | sed -e 's/*/\\*/g' \
    | sed -e 's/+/\\+/g' \
    | sed -e 's/?/\\?/g' \
    | sed -e 's/{/\\{/g' \
    | sed -e 's/}/\\}/g' \
    | sed -e 's/(/\\(/g' \
    | sed -e 's/)/\\)/g' \
    | sed -e 's/\[/\\[/g' \
    | sed -e 's/\]/\\]/g' \
    | sed -e 's/|/\\|/g' \
    | sed -e 's/^/"?/' \
    | sed -e 's/$/"?/'
}

##
# Get indent from string
# $1: string
##
get_indent(){
  echo "$1" | sed -E -e 's/^( *).+$/\1/'
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
# Add the directive at the end of spec section
##
add_directive_with_section() {
  local in_section=false
  local indent=""
  local not_added=true
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $section_start_pattern ]]; then
      in_section=true
      indent=$(get_indent "$line")
      section_end_pattern="^$indent</$section_name>"
    fi

    if $in_section && [[ "$line" =~ $section_end_pattern ]]; then
      echo "$indent    $directive$values"
      in_section=false
      not_added=false
    fi
    echo "$line"
  done

  if $not_added; then
    echo "<$section_name $(esc "$section_value")>"
    echo "    $directive$values"
    echo "</$section_name>"
  fi
}

##
# Set the values of a directive
##
set_directive() {
  directive_pattern="^ *$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $directive_pattern ]]; then
      echo "$(get_indent "$line")$directive$values"
    else
      echo "$line"
    fi
  done
}

##
# Sets the value of a directive within the specified section
##
set_directive_with_section() {
  directive_pattern="^ *$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^$(get_indent "$line")</$section_name>"
    fi

    if $in_section && [[ "$line" =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ "$line" =~ $directive_pattern ]]; then
      echo "$(get_indent "$line")$directive$values"
    else
      echo "$line"
    fi
  done
}

##
# Set the directive values at the end
##
set_section() {
  directive=$(echo "$directive" | sed -E -e 's/^<(.+)>$/\1/')
  directive_pattern="^ *<$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $directive_pattern ]]; then
      echo "$(get_indent "$line")<$directive$values>"
    else
      echo "$line"
    fi
  done
}

##
# Set the directive values at the end
##
set_section_with_section() {
  directive=$(echo "$directive" | sed -E -e 's/^<(.+)>$/\1/')
  directive_pattern="^ *<$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^$(get_indent "$line")</$section_name>"
    fi

    if $in_section && [[ "$line" =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ "$line" =~ $directive_pattern ]]; then
      echo "$(get_indent "$line")<$directive$values>"
    else
      echo "$line"
    fi
  done
}

##
# Comment out the specified directive
##
disable_directive() {
  directive_pattern="^ *$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $directive_pattern ]]; then
      echo "$line" | sed -E -e 's/^( *)(.+)$/\1#\2/'
    else
      echo "$line"
    fi
  done
}
##
# Comment out directives in the specified section
##
disable_directive_with_section() {
  directive_pattern="^ *$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^$(get_indent "$line")</$section_name>"
    fi

    if $in_section && [[ "$line" =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ "$line" =~ $directive_pattern ]]; then
      echo "$line" | sed -E -e 's/^( *)(.+)$/\1#\2/'
    else
      echo "$line"
    fi
  done
}

##
# enable the specified directive
##
enable_directive() {
  directive_pattern="^ *#$directive$with_values"
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $directive_pattern ]]; then
      echo "$line" | sed -E -e 's/^( *)#(.+)$/\1\2/'
    else
      echo "$line"
    fi
  done
}

##
# enable directives in the specified section
##
enable_directive_with_section() {
  directive_pattern="^ *#$directive$with_values"
  local in_section=false
  local line=""
  while IFS= read -r line; do
    if [[ "$line" =~ $section_start_pattern ]]; then
      in_section=true
      section_end_pattern="^$(get_indent "$line")</$section_name>"
    fi

    if $in_section && [[ "$line" =~ $section_end_pattern ]]; then
      in_section=false
    fi

    if $in_section && [[ "$line" =~ $directive_pattern ]]; then
      echo "$line" | sed -E -e 's/^( *)#(.+)$/\1\2/'
    else
      echo "$line"
    fi
  done
}
##
# Main
##
oldifs="$IFS"
operation="$1"
directive="$2"
directive_pattern=""
values=""
with_values=""
with_section=""
section_name=""
section_value=""
section_start_pattern=""
section_end_pattern=""
file_path=""
# print usage if no argument or help argument
if [ $# -eq 0 -o "$1" = 'help' -o "$1" = '--help' ]; then
  usage
  ok
fi
# Assign option value to variable
shift 2
while getopts v:w:s:f: OPT; do
  case $OPT in
    v) values+=" $(esc "$OPTARG")";;
    w) with_values+=" +$(regexp "$OPTARG")";;
    s) with_section="$OPTARG";;
    f) file_path="$OPTARG";;
  esac
done
# Create a section regular expression from the with_section variable
if [ -n "$with_section" ]; then
  if [[ "$with_section" = *":"* ]]; then
    section_name=$(echo "$with_section" | sed -E -e 's/^(.+):(.+)$/\1/')
    section_value=$(echo "$with_section" | sed -E -e 's/^(.+):(.+)$/\2/')
    section_start_pattern="^ *<$section_name +$(regexp "$section_value")"
  else
    section_name="$with_section"
    section_start_pattern="^ *<$section_name .+>"
  fi
fi
# Construct the name of the function to execute
func="$operation"
if [[ $directive =~ ^\<.+\>$ ]]; then
  func+="_section"
else
  func+="_directive"
fi
if [ -n "$with_section" ]; then
  func+="_with_section"
fi
# Rewrite the file if there is an file_path variable
if [ -n "$file_path" ]; then
  tmp_file=`cat /dev/urandom | base64 | fold -w 16 | head -n 1 | sed -e 's|/|-|'`
  cp -p "$file_path" "$tmp_file"
  $func < "$tmp_file" > "$file_path"
  rm -f "$tmp_file"
  ok
fi
# Piping if there is no file_path variable
$func
ok
