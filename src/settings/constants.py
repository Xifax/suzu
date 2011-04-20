# -*- coding: utf-8 -*-
'''
Created on Feb 26, 2011

@author: Yadavito
'''

"""Global/useful constants"""

# external #
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

# kanji info dialog
K_WIDTH = 500
K_HEIGHT = D_HEIGHT
K_INDENT = 2

# kanji groups dialog
G_WIDTH = 500
G_HEIGHT = D_HEIGHT
G_INDENT = 2

# status dialog
S_WIDTH = D_WIDTH
S_HEIGHT = 40
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
Q_HEIGTH = 365
Q_INDENT = Q_WIDTH - 300
Q_VINDENT = 56
Q_SPACE = 30

# tools 
T_WIDTH = 200
T_HEIGHT = 300

# quick load
L_WIDTH = 180
L_HEIGHT = 220

# browser
W_WIDTH = 800
W_HEIGHT = 600

###########################
### paths and resources ###
###########################

SQLITE = 'sqlite:///'
PATH_TO_RES = '../res/'
DBNAME = 'studying.db'
KANJIDIC2 = 'kanjidic2.db'
JMDICT = 'jmdict.db'
JMDICT_DUMP = 'jmdict.pck'
GROUPS_DUMP = 'groups.pck'
KANJI_MANIFEST = 'KANJI-MANIFEST-UNICODE-HEX'

ICONS = 'icons/'
LOGOS = 'logo/'
TRAY = 'tray/'
STROKES = 'kanji/'
IMAGES = 'images/'

NOW_ICON = 'now.png'
START_ICON = 'start.png'
PAUSE_ICON = 'pause.png'
OPTIONS_ICON = 'wrench.png'
ABOUT_ICON = 'info.png'
STAT_ICON = 'docs.png'
CLOSE_ICON = 'close.png'
DICT_ICON = 'dict.png'
LOAD_ICON = 'load.png'
UTILS_ICON = 'utils.png'

###########################
### version information ###
###########################

__version__ = '0.0.4'       #beware: is not imported with '*'
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

BUTTON_KANA_MAX = 5

###########################
###       sentences     ###
###########################

SENTENCE_MAX = 74
COLUMNS_MAX = 22
TRANSLATION_CHARS_LIMIT = 90
MIN_FONT_SIZE = 14

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
    
###########################
###       web urls      ###
###########################

NAVER_IMAGE_SEARCH = "http://search.naver.jp/image?q="

###########################
###        timers       ###
###########################

UPDATE_FREQ = 1000  #ms

###########################
###     achievements    ###
###########################

BIJIN = {
         0: (u'Sakamoto Maaya', u'坂本真綾'),
         1: (u'Kawamura Yukie', u'川村ゆきえ'),
         2: (u'Isihara Satomi', u'石原さとみ'),
         3: (u'Horikita Maki', u'堀北真希'),
         4: (u'Kago Ai', u'加護亜依'),
         5: (u'Isihara Satomi', u'石原さとみ'),
         6: (u'Hara Mikie', u'原幹恵'),
         7: (u'Nagasawa Masami', u'長澤まさみ'),
         8: (u'Aragaki Yui', u'新垣結衣'),
         9: (u'Yoshisawa Hitomi', u'吉澤ひとみ'),
         10: (u'Aibu Saki', u'相武紗季'),
         11: (u'Nakama Yukie', u'仲間由紀恵'),
         12: (u'Ueno Juri', u'上野樹里'),
         13: (u'Ayase Haruka', u'綾瀬はるか'),
         14: (u'Bae Doo-na', u'ペ・ドゥナ'),
         15: (u'Shida Mirai', u'志田未来'),
         16: (u'Tano Kii', u'北乃きい'),
         }

###########################
###        review       ###
###########################

MAX_REVIEW_ITEMS = 30