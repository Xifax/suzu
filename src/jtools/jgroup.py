# -*- coding: utf-8 -*-
'''
Created on Mar 30, 2011

@author: Yadavito
'''

# internal #
import sys, glob, pickle

# external #
from PyQt4.QtGui import QFileDialog, QApplication
from BeautifulSoup import BeautifulSoup

# own #
from settings.constants import PATH_TO_RES, GROUPS_DUMP

class KanjiGrouper:
    
    def __init__(self):
        self.groups = None
    
    def loadgroupsFromDump(self):
        dump = open(PATH_TO_RES + GROUPS_DUMP, 'r')
        self.groups = pickle.load(dump)
        dump.close()
    
    def findSimilarKanji(self, kanji):
        if self.groups is not None:
            return [group for group in self.groups if kanji in group]
         
def getHtmlListsFromDirectory(directory):
    file_list = glob.glob(directory + '\\vol?-?-list.html')
    return file_list

# parser #
def parseHtmlKanjiGroups(file):
    kanji_groups = []
    
    soup = BeautifulSoup(open(file).read())
    groups = soup.findAll('div', attrs={'class':'listPosition'})
    if len(groups) == 0:
        groups = soup.findAll('div', attrs={'class':'listPositionL3'})
        
    for group in groups:
        kanji_group = []
        for item in group.findAll('td', attrs={'class':'listKanji'}):
            kanji_group.append(item.find('a').contents.pop())
        kanji_groups.append(tuple(kanji_group))
        
    return kanji_groups

# pickler #
def dumpGroupsToFile(groups):
    file_path = QFileDialog.getSaveFileName(None, 'Save pickled list', PATH_TO_RES, 'Pickled (*.pck)')
#    sys.setrecursionlimit(8000)
    dump = open(file_path, 'w')
    pickle.dump(groups, dump)
    dump.close()

# parsing script #
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    directory = QFileDialog.getExistingDirectory(None, 'Select Kanji.Odyssey data folder')
    
    files = getHtmlListsFromDirectory(str(directory))   # from gui 'open directory' dialog
    groups = []                                         # list of similar kanji groups(tuples)
    
    for file in files:
        groups += parseHtmlKanjiGroups(file)
        
    # dump groups to pickled file
    dumpGroupsToFile(groups)


