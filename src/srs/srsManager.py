# -*- coding: utf-8 -*-
'''
Created on Feb 7, 2011

@author: Yadavito
'''

# own #
from jdict.db import DBoMagic
from jtools.jisho import JishoClient
from leitner import Leitner
from settings.constants import modes, modeByKey

# external #
from mParser.mecabTool import MecabTool
from jcconv import kata2hira

class srsScheduler:

    #NB: only kanji mode is working properly

    def __init__(self):
        self.db = DBoMagic()
        self.mode = modes.kanji
        
    def activeDB(self):
        return self.db
        
    def initializeCurrentSession(self, mode, sessionSize):
        self.currentItem = u''
        self.currentExample = u''
        self.db.setupDB()
        
        self.db.initializeCurrentSession(modeByKey(mode), sessionSize)
        self.mode = mode
        
    def endCurrentSession(self, stats):
        self.db.endCurrentSesion()
        self.db.saveSessionStats(stats)
        
    def getNextItem(self):
        """Get next quiz item reading, set current quiz item"""
        self.currentItem = self.db.getNextQuizItem()
        self.currentExample = u''
        #TODO: add check for NoneType
    
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

        self.currentExample = self.db.getExample(self.currentItem)
        if self.currentExample is not None:
            ## adding corresponding word to db
            #self.db.addWordToDb(self.currentItem, self.getWordFromExample())
            self.db.addWordToDbAndLinkToExample(self.currentItem, self.getWordFromExample(), self.currentExample)
            
            return self.currentExample.sentence
        else:
            return self.currentExample
    
    def parseCurrentExample(self):
        return MecabTool.parseToWordsOnly(self.currentExample.sentence)
    
    def getCurrentSentenceReading(self):
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
        self.currentItem.wrong_in_current_session = self.currentItem.wrong_in_current_session + 1
        
        self.db.updateQuizItem(self.currentItem)
        
    def answeredCorrect(self):
        if self.currentItem.leitner_grade != Leitner.grades.Shelved.index:
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
    
    def getWordNonInflectedForm(self, item):
        try:
            return MecabTool.parseToWordsFull(item)[0]['nform']
        except:
            return item
        
    def getWordPronounciation(self, item):
        try:
            return kata2hira(MecabTool.parseToWordsFull(item)[0]['pronunciation'])
        except:
            return item
    
    def getNextQuizTime(self):
        return self.currentItem.next_quiz.strftime('%d %b %H:%M:%S')#('%d %b %H:%M:%S (%Y)')
    
    def getLeitnerGradeAndColor(self):
        return {'grade' : str(self.currentItem.leitner_grade), 'name' : Leitner.grades[self.currentItem.leitner_grade].key, 'color' : Leitner.correspondingColor(self.currentItem.leitner_grade)}
