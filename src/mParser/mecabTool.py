# -*- coding: utf-8 -*-

import MeCab

class MecabTool:
    @staticmethod
    def parseToWordsFull(text):
        mecab = MeCab.Tagger("")
    
        mnode = mecab.parseToNode(text.encode('utf8'))
        word_array = []
    
        while mnode:
            infos = {}
            infos['word'] = mnode.surface.decode('utf8')
            feature = mnode.feature.decode('utf8')
            array = feature.split(",")
            infos['type'] = array[0]
            infos['dform'] = array[4]
            infos['reading'] = array[5]
            infos['self'] = array[6]
            infos['pronunciation'] = array[7]       #NB: somehow, error hath happened here
            if not infos['type'] == "BOS/EOS":
                word_array.append(infos)
            mnode = mnode.next
    
        return word_array
    
    @staticmethod
    def parseToWordsOnly(text):
        words = MecabTool.parseToWordsFull(text)
        result = []
        for w in words:
            result.append(w['word'])
            
        return result
    
    @staticmethod
    def parseToReadingsKana(text):
        words = MecabTool.parseToWordsFull(text)
        result = []
        for w in words:
            result.append(w['pronunciation'])
            
        return result    