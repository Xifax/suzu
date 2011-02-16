# -*- coding: utf-8 -*-
'''
Created on Feb 12, 2011

@author: Yadavito
'''

from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_, asc
from elixir import Entity,Field,Unicode,Integer,TIMESTAMP,ManyToMany,\
metadata,session,create_all,setup_all,BOOLEAN

#import time
from datetime import datetime, timedelta
import os.path
from random import shuffle, sample, randrange

from leitner import Leitner

class Kanji(Entity):
    character = Field(Unicode(1))
    tags = Field(Unicode(128))
    reading_kun = Field(Unicode(128))       #is this even necessary?
    reading_on = Field(Unicode(128))
    meaning = Field(Unicode(128))
    
    # srs params for kanji mode
    next_quiz = Field(TIMESTAMP)
    leitner_grade = Field(Integer)
    active = Field(BOOLEAN)
    current_session = Field(BOOLEAN)
    been_in_session = Field(Integer)        #for statistics and control
    
    # relationns
    example = ManyToMany('Example')
    word = ManyToMany('Word')
    
class Word(Entity):
    word = Field(Unicode(16))
    reading = Field(Unicode(16))
    meaning = Field(Unicode(128))
    
    # srs params for words mode
    next_quiz = Field(TIMESTAMP)
    leitner_deck = Field(Integer)
    active = Field(BOOLEAN)
    current_session = Field(BOOLEAN)
    been_in_session = Field(Integer) 
    
    # relations
    kanji = ManyToMany('Kanji')
    example = ManyToMany('Example') #is it correct?

class Example(Entity):
    sentence = Field(Unicode(256))
    translation = Field(Unicode(256))
    
    # relations
    kanji = ManyToMany('Kanji')
    word = ManyToMany('Word') #is it correct?

class DBoMagic:
    
    def __init__(self):
        self.dbname = 'studying.db'
        self.kanjidic2 = 'kanjidic2.db'
        self.sqite = 'sqlite:///'
        self.pathToRes = '../res/'      #purportedly, exe will be in bin or whatever (not on the same level as /res)
        
        self.metadata = metadata
        self.metadata.bind = self.sqite + self.pathToRes + self.dbname      #TODO add check up
        self.db = ()    #kanjidic2 db
        
    def setupDB(self):  
        """Initialize/read database on disk"""
        self.db = SqlSoup(self.sqite + self.pathToRes + self.kanjidic2)     #TODO: add check up
        setup_all()
        if not os.path.exists(self.pathToRes + self.dbname):
            create_all()
    
    def getNextQuizItem(self):          #mode and active check does not needed
        #TODO: implement witch great verve and so on!
        #selection = Kanji.query.filter_by(current_session = True).all()
        #selection.order_by(asc(Kanji.next_quiz))
        #selection = Kanji.query.filter_by(current_session = True).order_by(asc(Kanji.next_quiz)).all()
        #complicated!
        #item = selection.query.first()
        #for item in selection
        #TODO: check if item.next_quiz is the same for multiple items
        #...
        return  Kanji.query.filter_by(current_session = True).order_by(asc(Kanji.next_quiz)).first()
        
    # each time application is launched    (session_size from options) #mode for kanji, words or both
    def initializeCurrentSession(self, mode, sessionSize):
        if mode == 'kanji':
            selection = Kanji.query.filter_by(active = True).all()
        elif mode == 'words':
            selection = Word.query.filter_by(active = True).all()
        else:
            selection = () # Kanji && Words?
        
        n = sessionSize
        
        shuffle(selection)
        if n > len(selection) : n = len(selection)      # without any try's and ValueErrors
        random_selection = sample(selection, n)

        # serious stuff ahead!
        for item in random_selection:
            # mark n random items as 'current' 
            item.current_session = True
            
        session.commit()

    def endCurrentSesion(self):
        for kanji in Kanji.query.all():
            kanji.current_session = False
        for word in Word.query.all():
            word.current_session = False    
        
        session.commit()

    def updateQuizItem(self, item, newGrade, nextQuiz):
        
        item.leitner_grade = newGrade
        item.next_quiz = nextQuiz
        
        session.commit()
        
    def updateQuizItemByValue(self, itemValue, newGrade, nextQuiz):
        
        result = Kanji.query.filter_by(character = itemValue).all()
        if 2 > len(result) > 0:
            result[0].leitner_grade = newGrade
            result[0].next_quiz = nextQuiz
        else:
            result = Word.query.filter_by(word = itemValue).all()
            if 2 > len(result) > 0:
                result[0].leitner_grade = newGrade
                result[0].next_quiz = nextQuiz
                
        session.commit()
       
    def addKanjiToDb(self, character):
        Kanji(character = character)
        session.commit()
        
    def addSentenceToDb(self, kanji, sentence, translation):
        Kanji.query.filter_by(character = kanji).one().example.append(Example(sentence = sentence,translation = translation))          #or get_by
        #k.example.append(Example(sentence = sentence,translation = translation)) 
        session.commit()
    
    def addExamplesForKanji(self, kanji, examples):
        for example in examples:
            kanji.example.append(Example(sentence = example,translation = examples[example]))
        session.commit()
            
    def getExample(self, kanji):
        examples = kanji.example
        return examples[randrange(0, len(examples))]
        
    #TODO: throw away unneeded implementation
    def checkIfKanjiHasExamplesByValue(self, kanjiValue):
        try:
            if len(Kanji.query.filter_by(character = kanjiValue).one().example) > 0:
                return True
            else: 
                return False
        except NoResultFound:
            return False
        
    def checkIfKanjiHasWordsByValue(self, kanjiValue):
        try:
            if len(Kanji.query.filter_by(character = kanjiValue).one().word) > 0:
                return True
            else: 
                return False
        except NoResultFound:
            return False
        
    def checkIfKanjiHasWords(self, kanji):
        if len(kanji.word) > 0:
            return True
        else:
            return False
        
    def checkIfKanjiHasExamples(self, kanji):
        if len(kanji.example) > 0:
            return True
        else:
            return False
    
    def addItemsToDbJlpt(self, jlptGrade):
        try:
            jlptGrade = int(jlptGrade)
            if 0 < jlptGrade < 5:
                selection = self.db.character.filter(self.db.character.jlpt==jlptGrade).all()
                
                #time for next quiz
                now = datetime.now()
                
                jlpt = u'jlpt' + str(jlptGrade)
                
                for kanji in selection:
                    # VERY time consuming
                    #_now = time.time()
                    # in theory, it can be thrown away
                    readings_kun = self.db.reading.filter(and_(self.db.reading.fk==kanji.id, self.db.reading.type=='ja_kun')).all()
                    readings_on = self.db.reading.filter(and_(self.db.reading.fk==kanji.id, self.db.reading.type=='ja_on')).all()
                    meaning = self.db.meaning.filter(and_(self.db.meaning.fk==kanji.id, self.db.meaning.lang=='en')).all()
                    #_after = time.time()
                    
                    #sum += _after - _now
                    #print _after - _now
                
                    kun_string = u''
                    on_string = u''
                    meaning_string = u''
                
                    if len(readings_kun) > 0:
                        for kun in readings_kun:
                            kun_string += kun.value + ';'
                        
                    if len(readings_on) > 0:
                        for on in readings_on:
                            on_string += on.value + ';'
                    
                    if len(meaning) > 0:
                        for m in meaning:
                            meaning_string += m.value + ';'
                
                    Kanji(character = kanji.literal, tags = jlpt, reading_kun = kun_string, reading_on = on_string, meaning = meaning_string, 
                          next_quiz = now, leitner_grade = Leitner.grades.None.index, active = True)   #grade integer value
                    #next_quiz -> may be const = timedate.now()
                    
                    # for easier management
                    #Kanji(character = kanji.literal, tags = jlpt, next_quiz = now, leitner_grade = Leitner.grades.None.index, active = True)
                    
                try: 
                    session.commit()
                except IntegrityError:
                    print 'Already in db'
                    session.rollback()      #is it ok?
        except ValueError:
            print 'oops'    #TODO: add logger
            
        #def addKanjiToDb(self, kanji):
            #test = self.db.character.filter(self.db.character.literal = kanji).one()
'''
db = DBoMagic()
db.setupDB()

#jlptGrade = 3
#db.addItemsToDbJlpt(jlptGrade)

db.initializeCurrentSession('kanji', 300)
quiz = db.getNextQuizItem()
db.updateQuizItem(quiz, 2, datetime.now() + timedelta(hours=1))
nextQuiz = db.getNextQuizItem()
andOnceMore = db.getNextQuizItem()
#TODO: add resetting session
print 'yahoo!'
'''
'''
kanji = u'空'
db.addKanjiToDb(kanji)
if not db.checkIfKanjiHasExamples(kanji):
    db.addSentenceToDb(kanji, u'空は青いね', u'Sky is blue, isn''t it')
'''