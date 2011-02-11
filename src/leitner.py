# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2011

@author: Yadavito
'''

from enum import Enum
from datetime import datetime, timedelta

class Leitner:
    grades = Enum('None', 'SeenOnce', 'Familiar', 'Accustomed', 'Memorized', 'Digested', 'Learned', 'LongTerm', 'Shelved') #TODO: add some more
    
    coeff = 1.0
    
    #NB: algorithm should select from earliest date ever (even if already in past)
    
    @staticmethod
    def nextQuiz(grade):         # 'time' param not required, we're counting from 'now'
        return {
           Leitner.grades.None : datetime.now(),                                                # or it may be better to specify nothing at all
           Leitner.grades.SeenOnce : datetime.now() + timedelta(minutes = Leitner.coeff * 10),  #or 15, 30?
           Leitner.grades.Familiar : datetime.now() + timedelta(hours = Leitner.coeff * 1),     #or 2, 3?
           Leitner.grades.Accustomed : datetime.now() + timedelta(hours = Leitner.coeff * 12),
           Leitner.grades.Memorized : datetime.now() + timedelta(days = Leitner.coeff * 1),
           Leitner.grades.Digested : datetime.now() + timedelta(days = Leitner.coeff * 3),
           Leitner.grades.Learned : datetime.now() + timedelta(weeks = Leitner.coeff * 1),
           Leitner.grades.LongTerm : datetime.now() + timedelta(month = Leitner.coeff * 1),
           Leitner.grades.Shelved : datetime.now() + timedelta(month = Leitner.coeff * 6)       #or a full year?
        }[grade]