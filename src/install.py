# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2011

@author: Yadavito
'''

import sys, urllib, subprocess, os

def dlProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    sys.stdout.write("Download progress: %d%%   \r" % (percent) )
  
def downloadWithProgressbar(url):
    file_name = url.split('/')[-1]
    print 'Downloading ' + file_name
    urllib.urlretrieve(url, file_name, reporthook=dlProgress)
    return file_name

try:
    from setuptools.command import easy_install
except ImportError:
    print 'Please, install easy_install!'
    if raw_input('Download setuptools now? [y/n]: ') == 'y' or 'Y':
        file = downloadWithProgressbar('http://pypi.python.org/packages/2.6/s/setuptools/setuptools-0.6c11.win32-py2.6.exe')
        subprocess.call('./' + file)
        os.remove('./' + file)
    else: sys.exit(0)

def install_with_easyinstall(package):
    easy_install.main(["-U", package])
    
if __name__ == '__main__':

    packages = ['pyside', 'sqlalchemy', 'elixir', 'enum', 'userconfig', 'jcconv', 'uromkan', 'cjktools', 'cjktools-data', 'pywin32']
    for package in packages:
        print 'Installing ' + package
        install_with_easyinstall(package)
        
    print 'completed'
