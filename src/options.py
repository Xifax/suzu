# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2011

@author: Yadavito
'''

from userconfig import UserConfig
from about import __version__

class Options:
    
    def __init__(self):
        self.APP_NAME = 'suzu'             #輪廻／りんね or 鈴ね
        
        #default settings    #TODO: group fonts settings
        self.OPTIONS = [('SFont',           #sentences font
                {'name' : u'ヒラギノ丸ゴ Pro W4',
                 'size' : 18,
                 }),
                 ('QFont',                  #quiz answers font
                  {'name' : u'FOT-筑紫明朝 Pro LB',
                   'size' : 14,
                   }),
                  ('IFont',                  #messages font
                  {'name' : u'Cambria',
                   'size' : 12,
                   }),
                 ('Intervals',              #time constraints
                  {'repetition' : 1,        #minutes
                   'countdown'  : 30,       #seconds
                   }),
                 ('Active',                 #active tags and mode
                  {'tags' : [],             #tags names (as, jlpt2,3 etc)
                   'mode' : 'kanji',        #kanji, words or both
                   }),
                 ('Launch',                 #launch options
                  {'autoquiz'   : False,    #start quiz on launch
                   'splash'     : False,    #splash on start
                   }),
                 ('Session',                #session parameters
                  {'size'       : 300,      #number of items in session
                   'length'     : 600,      #maximum repetitions/day
                   }),
               ]
        
        #creates or reads from app.ini in Users/username/
        self.CONFIG = UserConfig(self.APP_NAME, self.OPTIONS, version=__version__)
        
    def getSentenceFont(self):
        return self.CONFIG.get('SFont', 'name')
    
    def getSentenceFontSize(self):
        return self.CONFIG.get('SFont', 'size')
    
    def getQuizFontSize(self):
        return self.CONFIG.get('QFont', 'size')
    
    def getMessageFont(self):
        return self.CONFIG.get('IFont', 'name')
    
    def getMessageFontSize(self):
        return self.CONFIG.get('IFont', 'size')
    
    def getRepetitionInterval(self):
        return self.CONFIG.get('Intervals', 'repetition')
    
    def getCountdownInterval(self):
        return self.CONFIG.get('Intervals', 'countdown')
    
    def getSessionSize(self):
        return self.CONFIG.get('Session', 'size')
    
    def isQuizStartingAtLaunch(self):
        return self.CONFIG.get('Launch', 'autoquiz')
    
    def getQuizMode(self):
        return self.CONFIG.get('Active', 'mode')