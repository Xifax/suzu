# -*- coding: utf-8 -*-
'''
Created on Apr 13, 2011

@author: Yadavito
'''

# internal #
import sys

# external #
from PySide.QtCore import *
from PySide.QtGui import *

# own #
from jdict.db import DBoMagic
from settings.constants import *

class QuizRehash(QDialog):
    def __init__(self, db, parent=None):
        super(QuizRehash, self).__init__(parent)
        
        self.db = db
        
        self.info = QLabel('Would you like to go back over the problematic items?')
        self.yes = QPushButton('Okay')
        self.no = QPushButton('Let me go!')
        
        self.kanji = QLabel(u'')
        self.compounds = QLabel(u'')
        self.reading = QLineEdit(u'')
        self.mark = QLabel(u'')
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.info, 0, 0, 1, 2)
        self.layout.addWidget(self.yes, 1, 0)
        self.layout.addWidget(self.no, 1, 1)
        
        self.layout.addWidget(self.kanji, 2, 0)
        self.layout.addWidget(self.compounds, 2, 1)
        self.layout.addWidget(self.reading, 3, 0)
        self.layout.addWidget(self.mark, 4, 0)
        
        self.setLayout(self.layout)
        
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    def initComposition(self):
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setWindowTitle('Quiz rehash')
        
    def initComponents(self):
        self.kanji.hide()
        self.compounds.hide()
        self.reading.hide()
        self.mark.hide()
    
    def initActions(self):
        self.no.clicked.connect(self.endRehash)
        self.yes.clicked.connect(self.beginRehash)
        
        self.reading.returnPressed.connect(self.checkAnswer)
        
    #-------------- actions -------------#
    
    def checkSessionResults(self):
        self.items = self.db.getProblematicItems()
        if self.items is not None:
            self.items_iterator = iter(self.items)
            self.exec_()
            
    def endRehash(self):
        self.done(0)
        
    def beginRehash(self):
        self.yes.hide()
        self.no.hide()
        self.info.hide()
        
        self.kanji.show()
        self.compounds.show()
        self.reading.show()
        
        self.nextItem()
        
    def checkAnswer(self):
        #if correct:
        #self.items.remove(correct_item)
        self.nextItem() #test
        
    def nextItem(self):
        try:
            item = self.items_iterator.next()
#            self.compounds.setText(' '.join(item.word.word))
        except StopIteration:
            self.items_iterator = iter(self.items)
            item = self.items_iterator.next()
        finally:
            if len(self.items) > 0:
                self.kanji.setText(item.character)
            else:
                print 'the end'
        
#    def showEvent(self, event):
        
    