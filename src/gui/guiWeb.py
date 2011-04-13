# -*- coding: utf-8 -*-
'''
Created on Apr 9, 2011

@author: Yadavito
'''
# internal
import sys

# external
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

# own
from settings.constants import NAVER_IMAGE_SEARCH, W_HEIGHT, W_WIDTH

class WebPage(QWidget):
    def __init__(self, parent=None):
        super(WebPage, self).__init__(parent)
        
        self.layout = QVBoxLayout()
        
        self.progress = QProgressBar()
        
        self.web = QWebView(self)
        
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.web)
        
        self.setLayout(self.layout)
        
        self.web.loadProgress.connect(self.updateStatus)
        self.web.loadStarted.connect(self.showStatus)
        self.web.loadFinished.connect(self.hideStatus)
        
        self.initComposition()
        self.initComponents()
        
    def initComposition(self):
        self.setWindowFlags(Qt.WindowMaximizeButtonHint & Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('Naver image search')
        self.setMinimumSize(W_WIDTH, W_HEIGHT)
        
        desktop = QApplication.desktop().screenGeometry()
        self.move((desktop.width() - W_WIDTH)/2, (desktop.height() - W_HEIGHT)/2)
    
    def initComponents(self):
        self.layout.setMargin(0)
        
        self.progress.setRange(0, 100)
        self.progress.setMaximumHeight(16)
        
        self.web.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        
    def searchImages(self, query):
        self.setWindowTitle(query)
        self.web.load(QUrl(NAVER_IMAGE_SEARCH + query))
        self.setWindowIcon(self.web.icon())
        
    def resizeEvent(self, event):
        self.web.resize(self.width(), self.height())
        
    def updateStatus(self, progress):
        self.progress.setValue(progress)
        
    def showStatus(self):
        self.progress.show()
        
    def hideStatus(self):
        self.progress.hide()
        self.web.show()
        
    def showEvent(self, event):
        self.web.hide()
    #NB: ...
    def closeEvent(self, event):
        self.hide()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    web = WebPage()
    web.show()
    
    web.searchImages(u'川村ゆきえ')
    
    sys.exit(app.exec_())