# -*- coding: utf-8 -*-
'''
Created on Feb 7, 2011

@author: Yadavito
'''
import urllib2, re#, thread
from BeautifulSoup import BeautifulSoup

class JishoClient:

    @staticmethod
    def getExamples(query):
        HREF_ITER = 'href'
        UN_URL_PART = '/kanji/details/'
        EX_FOUND = 'Found'
        JISHO_URL = 'http://jisho.org/sentences?jap='
        
        url =  JISHO_URL + query    #may be kanji or word
        
        soup = BeautifulSoup(urllib2.urlopen(url))  #TODO: add try - except (in case internets've died)
        
        check = soup.findAll('h2')
        if len(check) > 0 and len(check[0].contents) > 0:
            if EX_FOUND in check[0].contents[0]:
                
                sentences = soup.findAll('a', href=re.compile('/kanji/details'))
                translations = soup.findAll('td', attrs={'class':'english'})
                
                r_sent = []
                r_trans = []
                
                if len(sentences) == len(translations):
                    for sentence in sentences:
                        r_sent.append(sentence[HREF_ITER].replace(UN_URL_PART, ''))
                    for translation in translations:
                        r_trans.append(translation.contents[0].replace('\t',''))
                
                return dict(zip(r_sent, r_trans))