# find_replace
Recursive Find&Replace script with support of unix-like filename patterns.

------
## Arguments

--help, -h :
> shows script and arguments descriptions.

--regex, -r :
> switches to the regex mode instead of the literal mode by default.

path :
> absolute or relative path to the folder where matched strings
    should be replaced.

find_pattern :
> a pattern to be matched and replaced. It is recommended to embrace it with
    single quotes. If single quotes are contained in the pattern itself,
    embrace the pattern with double quotes.

replace_pattern :
> a pattern to be put in place of the matched one. Apply the same quotes
    rules to it as to find_pattern.

file_patterns :
> zero, one, or multiple unix-like filename patterns to filter out large
    files, backups, etc. It is recommended to embrace them with single quotes
    to avoid the bash auto-replacement described in notes.

------
## Notes

- The script works well with both Python2 and Python3.


- find_replace_tests.py is a unittest script to test the module. It must be placed in
the same folder as "find_replace".


- Bash auto-replaces filename patterns when they are passed as arguments to the
script. See the example below:

        File structure:
        /
        |_/test_folder
          |__1.php
          |__1.html
        |__index.html
        |__test.html
        |__find_replace
<br>

        find_replace test_folder pattern replacement *.php *.html  
<br>
    Bash will auto-replace *.html with ['index.html', 'test.html'] if they are
    located in the same directory where the user currently is, so better embrace
    filename patterns with single quotes:

        find_replace test_folder pattern replacement '*.php' '*.html'
<br>
    These file patterns will be passed to the script correctly: ['*.php', '*.html']
