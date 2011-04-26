# -*- coding: utf-8 -*-
'''
Created on Apr 24, 2011

@author: Yadavito
'''

# internal #
import os
import fnmatch

def walkIgnore(root, ignore):
    for path, subdirs, files in os.walk(root):
        subdirs[:] = [
            d for d in subdirs
            if d not in ignore ]
        yield path, subdirs, files

def Walk(root='.', recurse=True, pattern='*', ignore=[]):
    """
        Generator for walking a directory tree.
        Starts at specified root folder, returning files
        that match our pattern. Optionally will also
        recurse through sub-folders.
    """
    for path, subdirs, files in walkIgnore(root, ignore):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                yield os.path.join(path, name)
        if not recurse:
            break

def LOC(root='', ignore=[], recurse=True):
    """
        Counts lines of code in two ways:
            maximal size (source LOC) with blank lines and comments
            minimal size (logical LOC) stripping same

        Sums all Python files in the specified folder.
        By default recurses through subfolders.
    """
    count_mini, count_maxi = 0, 0
    for fspec in Walk(root, recurse, '*.py', ignore):
        skip = False
        for line in open(fspec).readlines():
            count_maxi += 1

            line = line.strip()
            if line:
                if line.startswith('#'):
                    continue
                if line.startswith('"""'):
                    skip = not skip
                    continue
                if line.startswith("'''"):
                    skip = not skip
                    continue
                if not skip:
                    count_mini += 1

    return count_mini, count_maxi

def show_results():
    ignore_list = []
    loc_result = LOC('./', ignore_list)
    print 'LOC (with blanks and comments): ', loc_result[1]
    print 'LOC (code only): ', loc_result[0]

if __name__ == '__main__':
    show_results()