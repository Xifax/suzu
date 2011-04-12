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
        
        self.startMusings = ()
        self.startQuiz = ()
        self.startPause = ()
        
        self.totalMusingsTime = timedelta(seconds = 0)
        self.totalPostQuizTime = timedelta(seconds = 0)
        
        self.totalQuizActiveTime = timedelta(seconds = 0)
        self.totalPauseTime = timedelta(seconds = 0)
        
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
        return time.strftime('%H:%M:%S', time.gmtime((datetime.now() - self.startedQuiz).seconds))
    
    def getMusingsTime(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.totalMusingsTime.seconds))
    
    def getQuizTime(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.totalPostQuizTime.seconds))
    
    def getPausedTime(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.totalPauseTime.seconds))
    
    def getQuizActive(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.totalPostQuizTime.seconds + self.totalMusingsTime.seconds))
    
    def getAverageMusingTime(self):
        if self.totalItemSeen != 0:
            return time.strftime('%M:%S', time.gmtime(self.totalMusingsTime.seconds/self.totalItemSeen))
        else: return '-:-'
        
    def getAveragePostQuizTime(self):
        if self.totalItemSeen != 0:
            return time.strftime('%M:%S', time.gmtime(self.totalPostQuizTime.seconds/self.totalItemSeen))
        else: return '-:-'
    
    def musingsStarted(self):
        self.startMusings = datetime.now()
        
    def musingsStopped(self):
        self.totalMusingsTime += datetime.now() - self.startMusings
        
    def postQuizStarted(self):
        self.startQuiz = datetime.now()
        
    def postQuizEnded(self):
        self.totalPostQuizTime += datetime.now() - self.startQuiz
        
    def pauseStarted(self):
        self.startPause = datetime.now()
        
    def pauseEnded(self):
        self.totalPauseTime += datetime.now() - self.startPause

    def calculateActiveTime(self):
        self.totalQuizActiveTime = self.totalPostQuizTime + self.totalMusingsTime