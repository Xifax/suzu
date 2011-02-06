# -*- coding: utf-8 -*-
'''
Created on Jan 31, 2011

@author: Yadavito
'''
'''
# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
 

# Create a Qt application 
app = QApplication(sys.argv)
# Create a Label and show it
label = QLabel("Hello World")
label.show()
# Enter Qt application main loop
app.exec_()
sys.exit()
'''

 
import sys
from PySide.QtCore import *
from PySide.QtGui import *
 
class Form(QFrame):
     
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.countdown = QProgressBar()
        #self.countdown.setOrientation(Qt.Vertical)
        self.countdown.setMaximumHeight(6)

        #self.sentence = QLabel(u"<font size=8>これはテストの" + "<b><font color='blue'>文</font></b>" + "であります</font>")
        self.sentence = QLabel(u"これはテストの" + "<font color='blue'>文</font>" + "でありますですですですですですですですですですでですですですです！")
        self.sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        #font = QFont(u'メイリオ', 12) #さざなみ明朝      #メイリオ
        #font.setStyleStrategy(QFont.PreferAntialias)
        #font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 90)
        self.sentence.setFont(QFont(u'メイリオ', 12))
        self.sentence.setWordWrap(True)

        #self.edit = QLineEdit("Write my name here")
        #self.button = QPushButton("Show Greetings")   
        self.var_1st = QPushButton(u"ぶん")
        self.var_2nd = QPushButton(u"とら")
        self.var_3rd = QPushButton(u"あい")
        self.var_4th = QPushButton(u"よう")

        # Create layouts and add widgets
        layout_vertical = QVBoxLayout()
        layout_horizontal = QHBoxLayout()
        #layout_global = QHBoxLayout()
        
        layout_horizontal.addWidget(self.var_1st)
        layout_horizontal.addWidget(self.var_2nd)
        layout_horizontal.addWidget(self.var_3rd)
        layout_horizontal.addWidget(self.var_4th)

        layout_vertical.addWidget(self.countdown)
        layout_vertical.addWidget(self.sentence)
        layout_vertical.addLayout(layout_horizontal)
        
        #layout_global.addLayout(layout_vertical)
        #layout_global.addWidget(self.countdown)
        
        #layout.addWidget(self.button)

        # Set dialog layout
        self.setLayout(layout_vertical)
        #self.setLayout(layout_global)
        
        # Add button signal to greetings slot
        #self.button.clicked.connect(self.greetings) #!!!
        
        #--> move config from main here N.B.
         
    # Greets the user
    #def greetings(self):
        #print ("Hello %s" % self.edit.text())
        
    def trayExit(self):
        sys.exit()
 
 
if __name__ == '__main__':

    #may or may not want to control dialog size according to text size
    D_WIDTH = 400
    D_HEIGHT = 136
    
    #down right corner position
    H_INDENT = D_WIDTH + 10 #indent from right
    V_INDENT = D_HEIGHT + 40 #indent from bottom

    # Create the Qt Application
    app = QApplication(sys.argv)
    app.setStyle('plastique')
    # Create and show the form
    
    # config should be moved
    desktop = app.desktop().screenGeometry()
    #may need calculating position according to the display size 
    
    form = Form()
    form.setFont(QFont(u'さざなみ明朝 ', 12))
    form.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT, D_WIDTH, D_HEIGHT))
    form.setWindowOpacity(0.88)
    
    #form.setWindowFlags(Qt.ToolTip)   #!!! or SplashScreen: 
    #Popup will vanish if user misses the button/window
    form.setWindowFlags(Qt.FramelessWindowHint) #and Qt.WindowStaysOnTopHint) #well, it's also possible to call .show() or .raise() when needed
    form.setFocusPolicy(Qt.StrongFocus)
    #border
    form.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
    #form.setLineWidth(1)
    #form.setMidLineWidth(2)
    trayIcon = QSystemTrayIcon(app)
    trayIcon.setIcon(QIcon('../resources/noren.ico')) #testing, testing - seems to be working (even png)
    menu = QMenu()
    quizAction = menu.addAction('Quiz me now!')
    optionsAction = menu.addAction('Options')
    menu.addSeparator()
    exitAction = menu.addAction('Exit')
    
    #app.connect(exitAction,SIGNAL('triggered()'), app.exit()) #does not work
    #exitAction.connect(form.trayExit())

    trayIcon.setContextMenu(menu)
    trayIcon.show()

    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
    
    #def menuExit(self):
        #app.exit()
