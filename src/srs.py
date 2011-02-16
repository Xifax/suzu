# -*- coding: utf-8 -*-
'''
Created on Feb 7, 2011

@author: Yadavito
'''

from db import Kanji,Word,Example,DBoMagic
from jisho import JishoClient
from mParser.mecabTool import MecabTool

class srsScheduler:

    def __init__(self):
        self.db = DBoMagic()
        
        #items in terms of db classes
        
    def initializeCurrentSession(self, mode, sessionSize):
        self.currentItem = u''
        self.currentExample = u''
        self.db.setupDB()
        self.db.initializeCurrentSession(mode, sessionSize)
        
    def endCurrentSession(self):
        self.db.endCurrentSesion()
        
    def getNextItem(self):
        """Get next quiz item reading, set current quiz item"""
        self.currentItem = self.db.getNextQuizItem()
        self.currentExample = u''
        
        return self.currentItem.character
    
    def getCurrentItem(self):
        return self.currentItem.character
    
    def getExample(self, item):
        return u'空は青いね'
     
    def getCurrentExample(self):
        if not self.db.checkIfKanjiHasExamples(self.currentItem):
            #NB: how about some threading and queues?
            #examples = JishoClient.getExamples(item)
            self.db.addExamplesForKanji(self.currentItem, JishoClient.getExamples(self.currentItem.character))

        self.currentExample =  self.db.getExample(self.currentItem) 
        return self.currentExample.sentence
        #return db.getExample(self.currentItem)            
    
    def parseCurrentExample(self):
        return MecabTool.parseToWordsOnly(self.currentExample.sentence)
    
    #TODO: work with EDICT and etc
    def getQuizVariants(self,item):
        return [u'そら',u'から',u'てら',u'くく',]
    
    def getCorrectAnswer(self,item):
        return u'そら'
    
    def getSentenceTranslation(self):
        return self.currentExample.translation
    
    def getCurrentSentenceTranslation(self):
        return self.currentExample.translation
    
    def geCurrentSentenceReading(self):
        return ''.join(MecabTool.parseToReadingsKana(self.currentExample.sentence))
'''
db = DBoMagic()
db.setupDB()
jlptGrade = 3
db.addItemsToDbJlpt(jlptGrade)
print db.checkIfKanjiHasExamplesByValue(u'画')
print 'lalala'
'''
'''
test = srsScheduler()
test.initializeCurrentSession('kanji', 300)
print test.getNextItem()
'''