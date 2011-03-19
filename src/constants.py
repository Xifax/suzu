# -*- coding: utf-8 -*-
'''
Created on Feb 26, 2011

@author: Yadavito
'''

"""Global/useful constants"""

from enum import Enum

##########################
### dialog positioning ###
##########################

# quiz dialog
D_WIDTH = 560
D_HEIGHT = 176
H_INDENT = D_WIDTH + 10 #indent from right
V_INDENT = D_HEIGHT + 40 #indent from bottom

# info dialog
I_WIDTH = 220
I_HEIGHT = D_HEIGHT
I_INDENT = 2

# status dialog
S_WIDTH = D_WIDTH
S_HEIGHT = 30
S_INDENT = I_INDENT
S_CORRECTION = 0

# options dialog
O_WIDTH = 360
O_HEIGHT = 550

# about dialog
A_WIDTH = 400
A_HEIGHT = 200

# options status dialog
OS_HEIGTH = 30
OS_INDENT = 2 

# quick dictionary        
Q_WIDTH = 700
Q_HEIGTH = 305
Q_INDENT = 400
Q_VINDENT = 56
Q_SPACE = 30

###########################
### paths and resources ###
###########################

SQLITE = 'sqlite:///'
PATH_TO_RES = '../res/'     #may change depending on nested folder level (e.g. srs/package/$.py)
DBNAME = 'studying.db'
KANJIDIC2 = 'kanjidic2.db'
JMDICT = 'jmdict.db'
JMDICT_DUMP = 'jmdict.pck'

###########################
### version information ###
###########################

__version__ = '0.0.1'       #beware: is not imported with '*'
__application__ = 'suzu'    #輪廻／りんね or 鈴ね

###########################
###    quiz generator   ###
###########################

KANA_TABLE  =  [u'あ', u'い', u'う', u'え', u'お',
                u'か', u'き', u'く', u'け', u'こ', 
                u'さ', u'し', u'す', u'せ', u'そ', 
                u'た', u'ち', u'つ', u'て', u'と', 
                u'な', u'に', u'ぬ', u'ね', u'の', 
                u'は', u'ひ', u'ふ', u'へ', u'ほ', 
                u'ま', u'み', u'む', u'め', u'も', 
                u'や', u'ゆ', u'よ', 
                u'ら', u'り', u'る', u'れ', u'ろ', 
                u'わ', u'を', u'ん',
        
                u'が', u'ぎ', u'ぐ', u'げ', u'ご', 
                u'ざ', u'じ', u'ず', u'ぜ', u'ぞ', 
                u'だ', u'ぢ', u'づ', u'で', u'ど', 
                u'ば', u'び', u'ぶ', u'べ', u'ぼ', 
                u'ぱ', u'ぴ', u'ぷ', u'ぺ', u'ぽ' ]

BUTTON_KANA_MAX = 6     #as of now - not in use

###########################
###      quiz modes     ###
###########################

modes = Enum('kanji', 'words', 'all')

def modeByKey(key):
    try:
        return { 
                    modes.kanji.key  : modes.kanji,
                    modes.words.key  : modes.words,
                    modes.all.key  : modes.all
                }[key]
    except KeyError:
        return modes.all