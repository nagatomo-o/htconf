# htconf

Command to Edit Apache configuration directives (stdin or file)

# Setup

### Bash

```
curl -o /usr/local/bin/htconf https://github.com/nagatomo-o/htconf/blob/main/src/bash/htconf.sh
chmod 755 /usr/local/bin/htconf
```
### Python

```
curl -o /usr/local/bin/htconf https://github.com/nagatomo-o/htconf/blob/main/src/python/htconf.py
chmod 755 /usr/local/bin/htconf
```

# Usage

```sh
htconf [operation] [NAME] [options]                 Read text from stdin and write to stdout
htconf [operation] [NAME] [options] -f [file]       Edit file
htconf --help                                       Usage output
```

## Arguments

```
    [operation]     [add,set,disable,enable]
    [NAME]          Directive name
                     (Add "<" ">" if section directive)
```

## Options
```
    -v VALUE        Value of the directive to set
    -w VALUE        Matching Directive Value
    -s SECTION      Matching Directive Section
                    Format: <Section Name>:<Section Value>
```

# Example

## Add directive
```sh
htconf add TraceEnable -v Off
```
```diff
+ TraceEnable Off
```

## Add directive with section
```sh
htconf add RewriteEngine -v On -s IfModule:mod_rewrite.c
```
```diff
+ <IfModule mod_rewrite.c>
+     RewriteEngine On
+ </IfModule>
```

## Set directive value with specified value
```sh
htconf set LoadModule -v alias_module -v modules/mod_alias2.so -w alias_module -w modules/mod_alias.so
```
```diff
- LoadModule alias_module modules/mod_alias.so
+ LoadModule alias_module modules/mod_alias2.so
```

## Set directive value with specified value and section
```sh
htconf set AllowOverride -v AuthConfig -v Options -w none -s Directory:/
```
```diff
  <Directory />
-     AllowOverride none
+     AllowOverride AuthConfig Options
      Require all denied
  </Directory>
```

## Commentout directives
```sh
htconf disable AddType
```
```diff
- AddType application/x-compress .Z
- AddType application/x-gzip .gz .tgz
+ #AddType application/x-compress .Z
+ #AddType application/x-gzip .gz .tgz
```

## Commentout directives with value
```sh
htconf disable AddType -w application/x-compress -w .Z
```
```diff
- AddType application/x-compress .Z
+ #AddType application/x-compress .Z
  AddType application/x-gzip .gz .tgz
```

## Commentout directives with value and section
```sh
htconf disable LogFormat -w "%h %l %u %t \"%r\" %>s %b" -w common -s IfModule:log_config_module
```
```diff
  <IfModule log_config_module>
      LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
-     LogFormat "%h %l %u %t \"%r\" %>s %b" common
+     #LogFormat "%h %l %u %t \"%r\" %>s %b" common
      CustomLog /proc/self/fd/1 common
  </IfModule>
```

## Uncomment directives
```sh
htconf enable AddType
```
```diff
- #AddType application/x-compress .Z
- #AddType application/x-gzip .gz .tgz
+ AddType application/x-compress .Z
+ AddType application/x-gzip .gz .tgz
```

## Uncomment directives with values
```sh
htconf enable AddType -w application/x-gzip -w .Z
```
```diff
  #AddType application/x-compress .Z
- #AddType application/x-gzip .gz .tgz
+ AddType application/x-gzip .gz .tgz
