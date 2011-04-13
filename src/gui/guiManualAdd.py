# -*- coding: utf-8 -*-
'''
Created on Mar 21, 2011

@author: Yadavito
'''

# own #
from settings.fonts import Fonts
from jtools.jisho import JishoClient 

# external #
from PySide.QtGui import *
from PySide.QtCore import *
from bzrlib.graph import SearchResult

#TODO: make kanji copiable

class ManualAdd(QDialog):
    def __init__(self, db,  parent=None):
        super(ManualAdd, self).__init__(parent)
        
        # internal references #
        self.problemKanji = None
        self.db = db
        
        self.mainLayout = QGridLayout()
        
        self.infoLabel = QLabel(u'')
        self.buttonAdd = QPushButton(u'Add manually')
        self.buttonInflect = QPushButton(u'Search inflected')
        self.buttonInactive = QPushButton(u'Set inactive')
        
        self.enterSentence = QTextEdit()
        self.enterTranslation = QTextEdit()
        self.addExample = QPushButton(u'Check and add')
        
        self.sentenceInfo = QLabel(u'Example sentence:')
        self.exampleInfo = QLabel(u'Translation:')
        
        self.mainLayout.addWidget(self.infoLabel, 0, 0, 1, 3)
        self.mainLayout.addWidget(self.buttonAdd, 1, 0)
        self.mainLayout.addWidget(self.buttonInflect, 1, 1)
        self.mainLayout.addWidget(self.buttonInactive, 1, 2)
        self.mainLayout.addWidget(self.sentenceInfo, 2, 0)
        self.mainLayout.addWidget(self.enterSentence, 3, 0, 2, 3)
        self.mainLayout.addWidget(self.exampleInfo, 5, 0,)
        self.mainLayout.addWidget(self.enterTranslation, 6, 0, 2, 3)
        self.mainLayout.addWidget(self.addExample, 8, 0, 1, 3)
        
        self.confirmInactive = QPushButton('Yes, make that item inactive!')
        self.mainLayout.addWidget(self.confirmInactive, 9, 0, 1, 3)
        
        self.possibleReading = QLineEdit()
        self.findExamples = QPushButton(u'Find examples')
        self.searchResult = QTextEdit()
        self.copyToManual = QPushButton(u'Copy to manual editing')
        self.addResults = QPushButton(u'Add found examples to db')
        
        self.mainLayout.addWidget(self.possibleReading, 10, 0, 1, 3)
        self.mainLayout.addWidget(self.findExamples, 11, 0, 1, 3)
        self.mainLayout.addWidget(self.searchResult, 12, 0, 1, 3)
        self.mainLayout.addWidget(self.copyToManual, 13, 0, 1, 3)
        self.mainLayout.addWidget(self.addResults, 14, 0, 1, 3)
        
        self.setLayout(self.mainLayout)
    
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    def initComposition(self):
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
    
    def initComponents(self):
        self.infoLabel.setFont(QFont('Calibri', 12))
        self.enterSentence.setFont(QFont(Fonts.MSMyoutyou, 14))
        self.enterTranslation.setFont(QFont('Cambria', 12))
        
        self.possibleReading.setFont(QFont(Fonts.MatisuMinoriyamatoProM, 14))
        self.searchResult.setFont(QFont(Fonts.MSMyoutyou, 14))
        
        self.buttonAdd.setCheckable(True)
        self.buttonInactive.setCheckable(True)
        self.buttonInflect.setCheckable(True)
        
        self.enterSentence.setHidden(True)
        self.enterTranslation.setHidden(True)
        self.addExample.setHidden(True)
        self.sentenceInfo.setHidden(True)
        self.exampleInfo.setHidden(True)
        
        self.possibleReading.setHidden(True)
        self.findExamples.setHidden(True)
        self.searchResult.setHidden(True)
        self.copyToManual.setHidden(True)
        self.addResults.setHidden(True)
        
        self.confirmInactive.setHidden(True)
        
        self.searchResult.setReadOnly(True)
        self.enterSentence.setToolTip(u'To add multiple examples: separate each sentence by newline')
        self.enterTranslation.setToolTip(u'To add multiple examples: separate each sentence by newline')
        
    def initActions(self):
        self.buttonAdd.clicked.connect(self.showInput)
        self.buttonInactive.clicked.connect(self.showInactiveConfirmation)
        self.buttonInflect.clicked.connect(self.showInflectOptions)
        
        self.addExample.clicked.connect(self.checkAndAddExample)
        self.confirmInactive.clicked.connect(self.setInactiveAndClose)
        
        self.findExamples.clicked.connect(self.findExamplesUsingJishoClient)
        self.copyToManual.clicked.connect(self.copyToManualInput)

    #--------------- actions -------------------#

    def setProblemKanji(self, kanji):
        '''Also updates dialog contens'''
        self.problemKanji = kanji
        
        self.infoLabel.setText("Alas, there were no examples for item <font style='font-family:" + Fonts.TukusiMyoutyouProLB + ";font-size: 16pt'>" 
                               + kanji.character + "</font> on the internets.")
        
    def showInput(self):
        if self.buttonAdd.isChecked():
            self.enterSentence.setVisible(True)
            self.enterTranslation.setVisible(True)
            self.addExample.setVisible(True)
            self.exampleInfo.setVisible(True)
            self.sentenceInfo.setVisible(True)
            
            self.buttonInflect.setEnabled(False)
            self.buttonInactive.setEnabled(False)
        else:
            self.enterSentence.setHidden(True)
            self.enterTranslation.setHidden(True)
            self.addExample.setHidden(True)
            self.sentenceInfo.setHidden(True)
            self.exampleInfo.setHidden(True)
            
            self.buttonInflect.setEnabled(True)
            self.buttonInactive.setEnabled(True)
            
            self.adjustSize()
            
    def showInflectOptions(self):
        if self.buttonInflect.isChecked():
            self.possibleReading.setVisible(True)
            self.findExamples.setVisible(True)
            self.searchResult.setVisible(True)
            self.copyToManual.setVisible(True)
            self.addResults.setVisible(True)
            
            self.buttonAdd.setEnabled(False)
            self.buttonInactive.setEnabled(False)
        else:
            self.possibleReading.setHidden(True)
            self.findExamples.setHidden(True)
            self.searchResult.setHidden(True)
            self.copyToManual.setHidden(True)
            self.addResults.setHidden(True)
            
            self.buttonAdd.setEnabled(True)
            self.buttonInactive.setEnabled(True)
            
            self.adjustSize()
    
    def showInactiveConfirmation(self):
        if self.buttonInactive.isChecked():
            self.confirmInactive.setVisible(True)
            self.buttonInflect.setEnabled(False)
            self.buttonAdd.setEnabled(False)
        else:
            self.confirmInactive.setHidden(True)
            
            self.buttonInflect.setEnabled(True)
            self.buttonAdd.setEnabled(True)
            
            self.adjustSize()
            
    def checkAndAddExample(self):
        sentences = self.enterSentence.toPlainText().split('\n')
        translations = self.enterTranslation.toPlainText().split('\n')
        
        examples = {}
        for sentence, translation in zip(sentences, translations):
            if sentence != '':
                if self.problemKanji.character in sentence:
                    examples[sentence] = translation
                else:
                    QMessageBox.information(self, u'Incorrect example', u'Entered sentence does not contain ' + self.problemKanji.character)
                    break
                    
        if len(examples) > 0:
            self.db.addExamplesForKanji(self.problemKanji, examples)
            self.done(0)
        else:
            QMessageBox.information(self, u'Failure', u'No examples added')
            
    def setInactiveAndClose(self):
        self.db.toggleActive(self.problemKanji)
        self.done(1)
        
    def findExamplesUsingJishoClient(self):
        self.searchResult.clear()
        
        lookup = JishoClient.getExamples(self.possibleReading.text())
        for item in lookup:
            self.searchResult.append('<b>' + item +'</b><br/>' + lookup[item] + '<br/>')
            
        self.adjustSize()

#        self.searchResult.resize(self.searchResult.width(), 30 * self.searchResult.toPlainText().count('\n'))
#        self.resize(self.width(), self.height() + self.searchResult.height()/2)
    
    def copyToManualInput(self):
        lookup = self.searchResult.toPlainText().split('\n')
        
        for index in range(0, len(lookup)):
            if index % 2 == 0:
                self.enterSentence.append(lookup[index].rstrip(u' '))
            else:
                self.enterTranslation.append(lookup[index].rstrip(u' '))  
        
        self.buttonInflect.click()
        self.buttonAdd.click()
        
        self.adjustSize()