# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2011

@author: Yadavito
'''

from userconfig import UserConfig

class Options:
    
    def __init__(self):
        #TODO: conceive application name
        self.APP_NAME = 'rinne'             #輪廻／りんね
        
        #default settings
        self.OPTIONS = [('SFont',           #sentences fonts
                {'name' : 'ヒラギノ丸ゴ Pro W4',
                 'size' : 18
                 }),
                 ('QFont',                  #quiz answers fonts
                  {'name' : '小塚明朝 Pro EL',
                   'size' : 16
                   }),
                 ('Intervals',              #time constraints
                  {'repetition' : 1,        #minutes
                   'countdown'  : 20        #seconds
                   }),
                 ('Active',                 #active tags and mode
                  {'tags' : [],             #tags names (as, jlpt2,3 etc)
                   'mode' : []              #kanji, words or both
                   }),
                 ('Launch',                 #launch options
                  {'autoquiz'   : False,    #start quiz on launch
                   'splash'     : False     #splash on start
                   })
               ]
        
        #creates or reads from app.ini in Users/username/
        self.CONFIG = UserConfig(self.APP_NAME, self.OPTIONS)