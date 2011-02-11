# -*- coding: utf-8 -*-
'''
Created on Feb 7, 2011

@author: Yadavito
'''

class srsScheduler:

    def __init__(self):
        self.currentItem = u''
        
    def getNextItem(self):
        #TODO: getting next item...
        self.currentItem = u'空'
        return u'空'
    
    def getCurrentItem(self):
        return self.currentItem
    
    def getExample(self,item):
        return u'空は青いね'
    
    def getQuizVariants(self,item):
        return [u'そら',u'から',u'てら',u'くく',]
    
    def getCorrectAnswer(self,item):
        return u'そら'
    
    def getSentenceTranslation(self,sentence):
        return u'translation!'
    
    def kanjiToKana(self,sentence):
        return u'test'