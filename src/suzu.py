# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2011

@author: Yadavito
@version: 0.0.3
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
# lxml
# OrderedDict
# BeautifulSoup

####################################
#            Resources             #
####################################

# MeCab parser
# Kanjidic2
# Jmdict
# Edict

####################################
#        Aptana built-ins:         #
####################################

# PySide
# elixir
# jcconv
# enum
# pkg_resources
# _MeCab
# ordereddict
# lxml

####################################
#    here goes global TODO list    #
####################################

# design
# TODO: kanji/word add notification
# TODO: prettify 'add' dialog
# TODO: show qdict found items count

# urgent
# TODO: fix 'pause time'

# concept

# functionality

# utilitarian

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
from gui.guiTools import Tools
from gui.guiWeb import WebPage
from gui.statGui import StatsInfo
from gui.guiRehash import QuizRehash
from utilities.utils import BackgroundDownloader
from utilities.log import log
from settings.optionsBackend import Options
from jdict.db import redict      # for redict, elusive import

####################################
#        QT application loop       #
####################################    

if __name__ == '__main__':

    app = QApplication(sys.argv)
    
    # application settings #
    options = Options()
    if options.isPlastique():  app.setStyle('plastique')
    
    # main gui module #
    quiz = Quiz(options)
    
    # additional gui components #
    about = About()
    options = OptionsDialog(quiz.srs.db, quiz.options)
    qdict = QuickDictionary(quiz.jmdict, quiz.edict, quiz.kjd, quiz.srs.db, quiz.options)
    
    # background updater #
    updater = BackgroundDownloader(quiz.options.getRepetitionInterval())
    updater.start()
    
    # additional tools #
    tools = Tools()
    web = WebPage()
    statistics = StatsInfo(quiz.srs.db)
    rehash = QuizRehash(quiz.srs.db, quiz.kjd)
    
    # initializing references and hotkeys #
    quiz.addReferences(about, options, qdict, updater, tools, statistics, web, rehash)
    quiz.initGlobalHotkeys()
    
    try:
        sys.exit(app.exec_())
    except Exception, e:
        log.debug(e)