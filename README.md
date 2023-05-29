# htconf

Command to Edit Apache configuration directives (stdin or file)

# Setup

### Bash

```sh
curl -Lf https://github.com/nagatomo-o/htconf/archive/v1.0.tar.gz | tar -zx --strip-component 1 htconf-1.0/htconf.sh
mv htconf.sh /usr/local/bin/htconf
chmod 755 /usr/local/bin/htconf
```
### Python

```sh
curl -Lf https://github.com/nagatomo-o/htconf/archive/v1.0.tar.gz | tar -zx --strip-component 1 htconf-1.0/htconf.py
mv htconf.py /usr/local/bin/htconf
chmod 755 /usr/local/bin/htconf
```

# Usage

```sh
htconf [operation] [NAME] [options]              Edit text as pipe
htconf [operation] [NAME] [options] -f [file]    Edit text file
htconf -e "[ARGS]" -e "[ARGS]" ...               Edit text with multiple operations as a pipe
htconf -e "[ARGS]" -e "[ARGS]" ... -f [file]     Edit text file with multiple operations
htconf --help                                    Show usage information
```

## Arguments

```
        operation     add, set, disable, enable
        NAME          Directive name
                      If it is a section directive name, enclose it with "<" and ">"
```

## Options
```
        -v VALUE      Value of the directive to set
        -w VALUE      Matching Directive Value
        -s SECTION    Matching Directive Section
                      Format: <Section Name>:<Section Value>
        -f FILE       Editing file
        -e ARGS       [operation] [NAME] [options] as string
```

# Example

## Edit text file with multiple operations
```sh
htconf -f /etc/httpd/conf/httpd.conf \
    -e "add Dir4 -v XXX" \
    -e "set Dir2 -v On -w None" \
    -e "set '<Sec2>' -v /var/www/html -w /var/www -s Sec1:/"
```

## Edit text with multiple operations as a pipe
```sh
cat /etc/httpd/conf/httpd.conf | htconf \
    -e "add Dir4 -v XXX" \
    -e "set Dir2 -v On -w None" \
    -e "set '<Sec2>' -v /var/www/html -w /var/www -s Sec1:/"
```

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

## Add directive value
```sh
htconf set "<Directory>" -v /var/www -w /
```
```diff
- <Directory />
+ <Directory /var/www>
      RewriteEngine On
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
htconf enable AddType -w application/x-gzip -w .gz
```
```diff
  #AddType application/x-compress .Z
- #AddType application/x-gzip .gz .tgz
+ AddType application/x-gzip .gz .tgz
```

## Uncomment directives and set new-value with values
```sh
htconf enable AddType -v .gz -v .tgz -v .tar.gz -w application/x-gzip -w .gz
```
```diff
  #AddType application/x-compress .Z
- #AddType application/x-gzip .gz .tgz
+ AddType application/x-gzip .gz .tgz .tar.gz
```

## Multiple Operation as pipe
```sh
htconf -e "enable AddType -w application/x-gzip" -e "set AddType -v application/gzip -v .gz -v .tgz -v .tar.gz -w application/x-gzip"
```
```diff
  AddType application/x-compress .Z
- #AddType application/x-gzip .gz .tgz
+ AddType application/x-gzip .gz .tgz .tar.gz
```
