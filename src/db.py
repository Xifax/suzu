# -*- coding: utf-8 -*-
'''
Created on Feb 12, 2011

@author: Yadavito
'''

from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from elixir import Entity,Field,Unicode,Integer,TIMESTAMP,ManyToMany,\
metadata,session,create_all,setup_all

#import time
import os.path

class Kanji(Entity):
    character = Field(Unicode(1))
    tags = Field(Unicode(128))
    reading_kun = Field(Unicode(128))
    reading_on = Field(Unicode(128))
    meaning = Field(Unicode(128))
    
    # srs params for kanji mode
    next_quiz = Field(TIMESTAMP)
    leitner_deck = Field(Integer)
    
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
        self.db = SqlSoup(self.sqite + self.pathToRes + self.kanjidic2)     #TODO: add check up
        setup_all()
        if not os.path.exists(self.pathToRes + self.dbname):
            create_all()
    
    def addItemsToDbJlpt(self, jlptGrade):
        try:
            jlptGrade = int(jlptGrade)
            if 0 < jlptGrade < 5:
                selection = self.db.character.filter(self.db.character.jlpt==jlptGrade).all()
                
                for kanji in selection:
                    # VERY time consuming
                    #_now = time.time()
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
                
                    Kanji(character = kanji.literal, tags = u'', reading_kun = kun_string, reading_on = on_string, meaning = meaning_string)
                    
                try: 
                    session.commit()
                except IntegrityError:
                    print 'Already in db'
                    session.rollback()      #is it ok?
        except:
            print 'oops'    #TODO: add logger
            
        def addSentenceToDb(self, kanji, sentence, translation):
            Kanji.query.filter_by(character=kanji).one().append(Example(sentence=sentence,translation=translation))         #or get_by
            session.commit()

#db = DBoMagic()
#db.setupDB()