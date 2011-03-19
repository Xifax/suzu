# -*- coding: utf-8 -*-
'''
Created on Feb 11, 2011

@author: Yadavito
'''

# internal #
from datetime import datetime, timedelta
# own #
from enum import Enum

class Leitner:
    #TODO: move to constants.py, really
    grades = Enum('None', 'SeenOnce', 'Familiar', 'Accustomed', 'Memorized', 'Digested', 'Learned', 'LongTerm', 'Shelved') #TODO: perhaps, add some more?
    #NB: enum objects must be compared by .index with integer values
    
    # scaling coefficient
    coeff = 1.0
    
    #NB: algorithm should select from earliest date ever (even if already in past)
    
    # accepts integer value
    # 'time' param not required, we're counting from 'now'
    @staticmethod
    def nextQuiz(grade):
        '''Time for next quiz, based on leitner grade (scaled by Leitner.coeff)'''
        return {
           Leitner.grades.None.index : datetime.now(),
           Leitner.grades.SeenOnce.index : datetime.now() + timedelta(minutes = Leitner.coeff * 20),  #or 15, 30?
           Leitner.grades.Familiar.index : datetime.now() + timedelta(hours = Leitner.coeff * 2),     #or 2, 3?
           Leitner.grades.Accustomed.index : datetime.now() + timedelta(hours = Leitner.coeff * 12),
           Leitner.grades.Memorized.index : datetime.now() + timedelta(days = Leitner.coeff * 1),
           Leitner.grades.Digested.index : datetime.now() + timedelta(days = Leitner.coeff * 3),
           Leitner.grades.Learned.index : datetime.now() + timedelta(weeks = Leitner.coeff * 1),
           Leitner.grades.LongTerm.index : datetime.now() + timedelta(weeks = Leitner.coeff * 4),      #timedelta does not accept months
           Leitner.grades.Shelved.index : datetime.now() + timedelta(weeks = Leitner.coeff * 24)       #or a full year?
        }[grade]
        
    @staticmethod
    def correspondingColor(grade):
        '''Color representation of lietner grade'''
        return {
           Leitner.grades.None.index : 'darkred',
           Leitner.grades.SeenOnce.index : 'red',
           Leitner.grades.Familiar.index : 'darksalmon',    #TODO: change color to something more visible
           Leitner.grades.Accustomed.index : 'orange',
           Leitner.grades.Memorized.index : 'khaki',
           Leitner.grades.Digested.index : 'gold',
           Leitner.grades.Learned.index : 'greenyellow',
           Leitner.grades.LongTerm.index : 'palegreen',
           Leitner.grades.Shelved.index : 'forestgreen'
        }[grade]