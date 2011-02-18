# -*- coding: utf-8 -*-
'''
Created on Feb 7, 2011

@author: Yadavito
'''

from db import Kanji,Word,Example,DBoMagic
from jisho import JishoClient
from mParser.mecabTool import MecabTool
from jcconv import kata2hira
from leitner import Leitner

class srsScheduler:

    #NB: only kanji mode is working properly

    def __init__(self):
        self.db = DBoMagic()
        
    def initializeCurrentSession(self, mode, sessionSize):
        self.currentItem = u''
        self.currentExample = u''
        self.db.setupDB()
        
        #FOR TEST DB INITIALIZATION ONLY
        #self.db.addItemsToDbJlpt(3)
        ######################
        
        self.db.initializeCurrentSession(mode, sessionSize)
        
    def endCurrentSession(self):
        self.db.endCurrentSesion()
        
    def getNextItem(self):
        """Get next quiz item reading, set current quiz item"""
        self.currentItem = self.db.getNextQuizItem()
        self.currentExample = u''
        #return self.currentItem.character
    
    def getCurrentItem(self):
        """Returns kanji itself"""
        return self.currentItem.character
    
    def getCurrentItemKanji(self):
        """Returns kanji with all information"""
        return self.currentItem
     
    def getCurrentExample(self):
        if not self.db.checkIfKanjiHasExamples(self.currentItem):
            #NB: how about some threading and queues?
            self.db.addExamplesForKanji(self.currentItem, JishoClient.getExamples(self.currentItem.character))

        self.currentExample =  self.db.getExample(self.currentItem) 
        return self.currentExample.sentence
    
    def parseCurrentExample(self):
        return MecabTool.parseToWordsOnly(self.currentExample.sentence)
    
    def geCurrentSentenceReading(self):
        return kata2hira(''.join(MecabTool.parseToReadingsKana(self.currentExample.sentence)))
    
    def getCurrentSentenceTranslation(self):
        return self.currentExample.translation

    def getQuizVariants(self):
        return self.db.findSimilarReading(self.getCorrectAnswer())
    
    '''    #does not parse the word itself 
    def getCorrectAnswer(self):
        return kata2hira(''.join(MecabTool.parseToReadingsKana(self.currentItem.character)))
    '''
    def answeredWrong(self):
        self.currentItem.leitner_grade = Leitner.grades.None.index
        self.currentItem.next_quiz = Leitner.nextQuiz(self.currentItem.leitner_grade)
        self.db.updateQuizItem(self.currentItem)
        
    def answeredCorrect(self):
        self.currentItem.leitner_grade = self.currentItem.leitner_grade + 1
        self.currentItem.next_quiz = Leitner.nextQuiz(self.currentItem.leitner_grade)
        self.db.updateQuizItem(self.currentItem)
    
    def getCorrectAnswer(self):
        words = MecabTool.parseToWordsFull(self.currentExample.sentence)
        answer = self.find(lambda word: self.currentItem.character in word['word'] , words)
        return kata2hira(answer['pronunciation'])
    
    def getWordFromExample(self):
        words = MecabTool.parseToWordsFull(self.currentExample.sentence)
        answer = self.find(lambda word: self.currentItem.character in word['word'] , words)
        return answer['word']
    
    # get reading based on word from parse results?
    def getWordPronunciationFromExample(self, item):
        words = MecabTool.parseToWordsFull(self.currentExample.sentence)
        answer = self.find(lambda word: item in word['word'] , words)
        return kata2hira(answer['pronunciation'])
    
    def find(self, f, seq):
        """Return first item in sequence where f(item) == True."""
        for item in seq:
            if f(item): 
                return item
            
    def getParsedExampleInFull(self):
        return MecabTool.parseToWordsFull(self.currentExample.sentence)
    
        
'''
srs = srsScheduler()
srs.initializeCurrentSession('kanji', 300)
print srs.getNextItem()
print srs.getCurrentExample()
answer = srs.getCorrectAnswer()
print answer
quiz = srs.getQuizVariants()
print ' '.join(quiz)
srs.answeredCorrect()
print '!'
'''