# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2011

@author: Yadavito
@version: 0.0.1
@license: GPL v3
@requires: Python 2.6.6
@requires: PySide 1.0.0
'''

# -> this is main application module <- #
#===============================================================================
# --- suzu ---
# -> main project file <-
# -> contains: 
#   - central GUI dialog
#   - TODO list
#   - dependencies & packages
#   - notes and iformation
# -> structure:
#   - gui ~ Qt frontend
#   - settings ~ options backend, constants
#   - srs ~ spaced repetition scheduler, db interface
#   - utilities ~ useful utilites
#   - jtools ~ jisho examples downloader
#   - jdict ~ db aggregator
#   - mParser ~ interface to mecab parser 
# -> dependencies setup:
#   - python install.py
# -> launch:
#   - python suzu.py
#===============================================================================

####################################
#            Dependencies          #
####################################

# PySide 1.0.0
# SQLAlchemy 0.6.6
# Elixir
# UserConfig
# MeCab
# Uromkan                http://goo.gl/NofcO
# Jcconv 0.1.6
# Cjktools
# Cjktools-data

####################################
#            Resources             #
####################################

# MeCab parser
# Kanjidic2
# Jmdict

####################################
#        Aptana built-ins:         #
####################################

# PySide
# elixir
# jcconv
# enum
# pkg_resources

####################################
#    here goes global TODO list    #
####################################

# urgent
# TODO: control case when there's no examples at all
# TODO: implement jisho kana search for rare kanji
# LATER: change button font size depending on number of characters (< 5)
# TODO: add additional info dialog, briefly describing each kanji in compound

# concept
# TODO: implement 'similar kanji' system, based on comparing number of similar rads in RadDict

# functionality
# ...

# utilitarian
# TODO: errors logging

####################################
#            Imports               #
####################################

# internal packages #
import sys

# external packages #
from PySide.QtGui import QApplication

# own packages #
from gui.guiMain import Quiz
from gui.about import About
from gui.guiOpt import OptionsDialog
from gui.guiQuick import QuickDictionary
from utilities.utils import BackgroundDownloader
from jdict.db import redict      # for redict, elusive import

####################################
#        QT application loop       #
####################################    

if __name__ == '__main__':

    app = QApplication(sys.argv)
    
    quiz = Quiz()
    if quiz.options.isPlastique():  app.setStyle('plastique')
    
    about = About()
    options = OptionsDialog(quiz.srs.db, quiz.options)
    qdict = QuickDictionary(quiz.jmdict, quiz.edict, quiz.kjd, quiz.srs.db, quiz.options)
        
    updater = BackgroundDownloader(quiz.options.getRepetitionInterval())
    updater.start()
    
    quiz.addReferences(about, options, qdict, updater)
    quiz.initGlobalHotkeys()
    
    sys.exit(app.exec_())