# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2011

@author: Yadavito
'''

from userconfig import UserConfig
from constants import __version__#,__application__

class Options:
    
    def __init__(self):
        #self.APP_NAME = __application__
        self.APP_NAME = 'suzu'
        
        #default settings    #TODO: group fonts settings
        self.OPTIONS = [('SFont',           #sentences font
                {'name' : u'ヒラギノ丸ゴ Pro W4',
                 'size' : 18,
                 }),
                 ('QFont',                  #quiz answers font
                  {'name' : u'FOT-筑紫明朝 Pro LB',
                   'size' : 12,
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
                ('Runtime',                 #runtime options
                  {'ontop'      : True,     #always on top
                   'global'     : True,     #enable global hotkeys
                   'log'        : False,    #enable errors logging
                   'sound'      : False,    #enable sound
                   'fade'       : True,     #enable fade effect
                   }),
                 ('Session',                #session parameters
                  {'size'       : 300,      #number of items in session
                   'length'     : 600,      #maximum repetitions/day
                   }),
                 ('Dict',                   #dictionary options
                  {'lang'       : 'eng',    #translation language
                   }),
               ]
        
        #creates or reads from app.ini in Users/username/
        self.CONFIG = UserConfig(self.APP_NAME, self.OPTIONS, version=__version__)
    ### fonts ###
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
    
    ### intervals ###
    def getRepetitionInterval(self):
        return self.CONFIG.get('Intervals', 'repetition')
    
    def getCountdownInterval(self):
        return self.CONFIG.get('Intervals', 'countdown')
    
    def setRepetitionInterval(self, interval):
        self.CONFIG.set('Intervals', 'repetition', interval)
    
    def setCountdownInterval(self, interval):
        self.CONFIG.set('Intervals', 'countdown', interval)
    
    ### session ###
    def getSessionSize(self):
        return self.CONFIG.get('Session', 'size')
    
    def getSessionLength(self):
        return self.CONFIG.get('Session', 'length')
    
    def setSessionSize(self, number):
        self.CONFIG.set('Session', 'size', number)
    
    def setSessionLength(self, number):
        self.CONFIG.set('Session', 'length', number)
    
    ### launch ###
    def isQuizStartingAtLaunch(self):
        return self.CONFIG.get('Launch', 'autoquiz')
    
    def setQuizStartingAtLaunch(self, flag):
        self.CONFIG.set('Launch', 'autoquiz', flag)
        
    def isSplashEnabled(self):
        return self.CONFIG.get('Launch', 'splash')
    
    def setSplashEnabled(self, flag):
        return self.CONFIG.get('Launch', 'splash', flag)
    
    ### quiz ###
    def getQuizMode(self):
        return self.CONFIG.get('Active', 'mode')
    
    ### runtime ###
    def isAlwaysOnTop(self):
        return self.CONFIG.get('Runtime', 'ontop')
        
    def isSoundOn(self):
        return self.CONFIG.get('Runtime', 'sound')
    
    def isGlobalHotkeyOn(self):
        return self.CONFIG.get('Runtime', 'global')
    
    def isLoggingOn(self):
        return self.CONFIG.get('Runtime', 'log')
        
    def isFadeEffectOn(self):
        return self.CONFIG.get('Runtime', 'fade')
    
    def setAlwaysOnTop(self, flag):
        self.CONFIG.set('Runtime', 'ontop', flag)
        
    def setSoundOn(self, flag):
        self.CONFIG.set('Runtime', 'sound', flag)
    
    def setGlobalHotkeyOn(self, flag):
        self.CONFIG.set('Runtime', 'global', flag)
    
    def setLoggingOn(self, flag):
        return self.CONFIG.set('Runtime', 'log', flag)
        
    def setFadeEffectOn(self, flag):
        return self.CONFIG.set('Runtime', 'fade', flag)