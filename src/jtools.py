# -*- coding: utf-8 -*-
'''
Created on Feb 16, 2011

@author: Yadavito
'''

import urllib2
from xml.etree import ElementTree
from jcconv import kata2hira

class MecApiClient:
    
    @staticmethod
    def getKanaReading(query):
        MECAPI_URL = u'http://mimitako.net/api/mecapi.cgi?sentence='
        OPTIONS = u'&response=pronounciation'
        XML_TAG = u'word/pronounciation'
        
        url = MECAPI_URL + query + OPTIONS
        result = urllib2.urlopen(url)

        tree = ElementTree.fromstring(result.read())
        reading = []
        
        for node in tree.findall(XML_TAG):
            reading.append(node.text)
        
        return kata2hira(''.join(reading))