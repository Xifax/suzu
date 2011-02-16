# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2011

@author: Yadavito
'''

from enum import Enum
from datetime import datetime, timedelta

class Leitner:
    grades = Enum('None', 'SeenOnce', 'Familiar', 'Accustomed', 'Memorized', 'Digested', 'Learned', 'LongTerm', 'Shelved') #TODO: add some more
    #NB: enum must be compared by .index
    
    coeff = 1.0
    
    #NB: algorithm should select from earliest date ever (even if already in past)
    
    #accepts integer value
    @staticmethod
    def nextQuiz(grade):         # 'time' param not required, we're counting from 'now'
        return {
           Leitner.grades.None.index : datetime.now(),  # it's not necessary to fill in the corresponding db field  # or it may be better to specify nothing at all
           Leitner.grades.SeenOnce.index : datetime.now() + timedelta(minutes = Leitner.coeff * 10),  #or 15, 30?
           Leitner.grades.Familiar.index : datetime.now() + timedelta(hours = Leitner.coeff * 1),     #or 2, 3?
           Leitner.grades.Accustomed.index : datetime.now() + timedelta(hours = Leitner.coeff * 12),
           Leitner.grades.Memorized.index : datetime.now() + timedelta(days = Leitner.coeff * 1),
           Leitner.grades.Digested.index : datetime.now() + timedelta(days = Leitner.coeff * 3),
           Leitner.grades.Learned.index : datetime.now() + timedelta(weeks = Leitner.coeff * 1),
           Leitner.grades.LongTerm.index : datetime.now() + timedelta(weeks = Leitner.coeff * 4),      #timedelta does not accept months
           Leitner.grades.Shelved.index : datetime.now() + timedelta(weeks = Leitner.coeff * 24)       #or a full year?
        }[grade]