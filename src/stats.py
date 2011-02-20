# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2011

@author: Yadavito
'''

#TODO: statistics gatherer & miner (as time spent on musing, total time, etc) + problem items + unique items
from datetime import timedelta, datetime
import time

class Stats():
    
    def __init__(self):
        self.totalItemSeen = 0
        self.answeredCorrect = 0
        self.startedQuiz = datetime.now()
        
        self.totalMusingsTime = timedelta(seconds = 0)
        self.averageMusingsTime = timedelta(seconds = 0)
        self.totalPostQuizTime = timedelta(seconds = 0)
        self.averagePostQuizTime = timedelta(seconds = 0)
        
    def quizAnsweredCorrect(self):
        self.totalItemSeen = self.totalItemSeen + 1
        self.answeredCorrect = self.answeredCorrect + 1
        
    def quizAnsweredWrong(self):
        self.totalItemSeen = self.totalItemSeen + 1
        
    def getIncorrectAnswersCount(self):
        return str(self.totalItemSeen - self.answeredCorrect)
    
    def getCorrectRatioPercent(self):
        if self.totalItemSeen == 0: return '0%'
        else: return str(round(float(self.answeredCorrect)/float(self.totalItemSeen), 4) * 100) + '%'
        
    def getRunningTime(self):
        #return str(datetime.now() - self.startedQuiz)
        return time.strftime('%H:%M:%S', time.gmtime((datetime.now() - self.startedQuiz).seconds))