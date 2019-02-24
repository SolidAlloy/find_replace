#!/usr/bin/env python

from __future__ import print_function

import unittest
import subprocess as subproc
import os
import shutil
import imp

curdir = os.path.abspath(os.path.dirname(__file__))
# cannot import find_replace directly because it doesn't have the .py extension
find_replace = imp.load_source('find_replace',
                               os.path.join(curdir, 'find_replace'))
from find_replace import PermissionError


class FindReplaceTest(unittest.TestCase):
    """
    unittest class to test the find_replace functionality.

    Methods
    --------
    setUp :
        creates a directory and files to test find_replace
    tearDown :
        removes the test directory recursively
    reset :
        removes the directory, then creates again. Required to test
        find_replace several times within one test.
    add_hundred_files :
        adds hundred empty files into the test directory to test if the
        percentage is shown correctly in such case.
    replace_case :
        runs the find_replace.find_replace() function with different arguments
        and checks returned values for mistakes.
    test_replace :
        runs find_replace.find_replace() with and without regex mode and tests
        returned values.
    get_output :
        runs find_replace script with different arguments and returns output.
    check_percent_output :
        runs find_replace script and checks if the output equals the expected
        one.
    test_percentage :
        runs find_replace script with below and above 100 files and checks if
        "Progress: 100%" is in output.
    test_warning :
        runs find_replace script with no filename patterns and checks if the
        warning is shown.
    test_file_patterns :
        runs the find_replace.find_replace() function with 0, 1, and 2 filename
        patterns. Checks if the output is correct.
    test_stats_saving :
        must be run under root or a sudo user. If another user is specified,
        creates and operates on a file created under that user, then checks
        that the owner and permissions were left intact after the replacement.

    Attributes
    -----------
    str curdir :
        The directory where the script is executed.
    str path :
        The path to a test directory.
    list files_list :
        The list of paths to the test files.

    Notes
    ------
    Put the script in the same folder as "find_replace" to run tests.
    """
    def __init__(self, *args, **kwargs):
        # unittest.TestCase has its own __init__()
        # Format of super() is compatible with Python2 and Python3
        super(FindReplaceTest, self).__init__(*args, **kwargs)
        self.curdir = os.path.abspath(os.path.dirname(__file__))
        self.path = os.path.join(self.curdir, 'test_data')
        files_list = ['1.php', '2.php', '3.php', 'test_data2/4.php', '1.html',
                      '2.html', '3.html', 'test_data2/4.html', '1.txt',
                      '2.txt', '3.txt', 'test_data2/4.txt']
        self.files_list = [
            os.path.join(self.path, file) for file in files_list]

    def setUp(self):
        """
        Creates the following data tree:
        /
        |_/test_data
          |__1.html --- doesn't contain searched pattern
          |__1.php  --- doesn't contain searched pattern
          |__1.txt  --- doesn't contain searched pattern
          |__2.html --- has insufficient permissions
          |__2.php  --- has insufficient permissions
          |__2.txt  --- has insufficient permissions
          |__3.html
          |__3.php
          |__3.txt
          |_/test_data2
            |__4.html
            |__4.php
            |__4.txt
        """
        try:
            os.mkdir(self.path)
        except OSError:
            self.tearDown()
            os.mkdir(self.path)
        os.mkdir(self.path + '/test_data2')
        for file in self.files_list:
            with open(os.path.join('test_data', file), 'w') as f:
                if '1' in file:
                    f.write('test test\ntest\n')
                else:
                    f.write('test find test\nfind test\n')
            if '2.' in file:
                os.chmod(file, 0o111)

    def tearDown(self):
        """ removes the test directory recursively """
        shutil.rmtree(self.path)

    def reset(self):
        """ recreates starting setup """
        self.tearDown()
        self.setUp()

    def add_hundred_files(self):
        """ adds hundred files from 5.php to 104.php """
        for number in range(5, 105):
            file = os.path.join(self.path, str(number)+'.php')
            with open(file, 'w') as f:
                f.write('test')

    def replace_case(self, path, find, regex, file_patterns,
                     expected_occurences, expected_skipped, expected_filtered,
                     expected_changed_files):
        """ tests if find_replace.find_replace() returns correct values """
        replace = 'found '
        occurences, skipped, filtered = find_replace.find_replace(
            path, find, replace, regex, file_patterns, testing=True)
        self.assertEqual(occurences, expected_occurences)
        self.assertEqual(skipped, expected_skipped)
        self.assertEqual(filtered, expected_filtered)
        changed_files = 0
        # go trough all files and count changed ones.
        for file in self.files_list:
            try:
                with open(file) as f:
                    if f.read() == 'test found test\nfound test\n':
                        changed_files += 1
            except IOError:
                continue
        self.assertEqual(changed_files, expected_changed_files)

    def test_replace(self):
        """ tests find_replace.find_replace with regex On and Off """
        # checks that occurences were corectly replaced
        # verifies number of occurences
        # verifies number of skipped
        # verifies number of changed files
        self.replace_case(
            self.path, 'find ', False, ['*.php', '*.html'], 8, 2, 8, 4)
        self.reset()
        self.replace_case(
            self.path, r'f[i,o]n?d\s', True, ['*.php', '*.html'], 8, 2, 8, 4)

    def get_output(self, file_patterns):
        """
        Gets output of the script and tranforms from byte string to a regular
        string.
        """
        # {0} is for really old versions of Python
        output = subproc.check_output(
            "cd {0} && ./find_replace {1} find found {2}".format(
                self.curdir, self.path, file_patterns), shell=True)
        return output.decode()

    def check_percent_output(self, total_files):
        """
        Verifies that the output contains "Progress: 100%" and is in general
        correct.
        """
        output = self.get_output("'*.php' '*.html'")
        # find Progress: 100%
        pos = output.find('Progress: 100%')
        if pos != -1:
            # cut off all other percent numbers
            output = output[pos:]
        else:
            self.fail('No "Progress: 100%" found in output')
        expected_output = 'Progress: 100%\n\nOccurences replaced: 8\nFiles' + \
                          ' skipped (Permission denied): 2\nTotal files ' + \
                          'searched: {0}\n'.format(total_files)
        self.assertEqual(output, expected_output)

    def test_percentage(self):
        """ tests the script with below and above 100 files """
        # test with less than 100 files
        # test with above 100 files
        self.check_percent_output(8)
        self.reset()
        self.add_hundred_files()
        self.check_percent_output(108)

    def test_warning(self):
        """
        Tests that the warning is shown when no file patterns are passed to the
        script.
        """
        output = self.get_output('')
        self.assertIn(
            '** Consider using file patterns to speed up the process **',
            output)

    def test_file_patterns(self):
        """
        Checks that the values returned by find_replace.find_replace() are
        correct with 0, 1, and multiple filename patterns.
        """
        file_patterns = []
        self.replace_case(
            self.path, 'find ', False, file_patterns, 12, 3, 12, 6)
        self.reset()
        file_patterns = ['*.php']
        self.replace_case(self.path, 'find ', False, file_patterns, 4, 1, 4, 2)
        self.reset()
        file_patterns = ['*.php', '*.html']
        self.replace_case(self.path, 'find ', False, file_patterns, 8, 2, 8, 4)

    def test_stats_saving(self):
        """
        Checks that find_replace.find_replace() saves permissions and owner of
        a file when the script is run under another user.
        !!! Run this test under root or a sudo user !!!
        """
        try:
            os.mkdir('/etc/foo')
            shutil.rmtree('/etc/foo')
        except (PermissionError, OSError):  # PermissionError is for Python3,
            # OSError is for Python2
            self.fail('This test case can be run by root or sudoer only')

        user_path = '/home/cp_user'  # insert any existing user here
        user_stat = os.stat(user_path)
        user_uid, user_gid = user_stat[4], user_stat[5]
        filename = 'test_stats_saving.txt'  # must be unique because
        # find_replace looks for this filename recursively
        filepath = os.path.join(user_path, filename)
        with open(filepath, 'w') as f:
            f.write('find ')
        os.chown(filepath, user_uid, user_gid)
        # changed files = 0 because self.replace_case() is looking for changed
        # files only in the test_data directory
        self.replace_case(user_path, 'find ', False, ['test_stats_saving.txt'],
                          1, 0, 1, 0)
        file_stat = os.stat(filepath)
        file_uid, file_gid = file_stat[4], file_stat[5]
        self.assertEqual((user_uid, user_gid), (file_uid, file_gid))
        os.remove(filepath)


if __name__ == '__main__':
    unittest.main(verbosity=2)
