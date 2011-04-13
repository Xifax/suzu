# -*- coding: utf-8 -*-
'''
Created on Apr 9, 2011

@author: Yadavito
'''

# internal
import os, urllib2, StringIO, random
from urllib import urlretrieve
import urlparse

#external
from lxml import etree
from BeautifulSoup import BeautifulSoup

# own
from settings.constants import PATH_TO_RES, IMAGES, BIJIN
from utilities.log import log

class Achievements:
    def __init__(self):
        self.score = 0
        self.threshold = 10
        self.achieved = None
        self.alreadySeen = []
    
    def correctAnswer(self):
        self.score += 1
        if self.score == self.threshold:
            self.threshold *= 2
            self.achieved = self.randomBijin()
            self.score = 0
        else:
            self.achieved = None
        
    def wrongAnswer(self):
        self.score -= 1
        
    def randomBijin(self):
        tries = 0
        
        while tries <= len(BIJIN.keys()):
            index = random.randrange(1, len(BIJIN.keys()))
                                     
            if index not in self.alreadySeen:
                break
            else:
                tries += 1
                
        self.alreadySeen.append(index)
        return BIJIN[index]
    
    @staticmethod
    def nameToTag(name):
        return name.replace(' ', '_').lower()
    
BEHOIMI_MAIN = "http://behoimi.org/post/index.xml?limit="
BEHOIMI_QUERY = "&commit=Search&tags="
BEHOIMI_POST = "http://behoimi.org/post/show/"

class ImageGetter:
    @staticmethod
    def getBijinImages(name, limit):
        
        url =  BEHOIMI_MAIN + str(limit) + BEHOIMI_QUERY + name
        
        try:
            responseTree = etree.parse(StringIO.StringIO(urllib2.urlopen(url).read()))
            posts = responseTree.findall('post')
            for post in posts:
                image_url = post.get('file_url')
                
                image_name = image_url.split('/')[-1]
                
#                http://behoimi.org/data/ad/8b/ad8bf4363dd992abae9bb672bc499d4c.jpg
#                http://behoimi.org/data/sample/ad/8b/samplead8bf4363dd992abae9bb672bc499d4c.jpg
                
                #===============================================================
                # post_url = BEHOIMI_POST + post.get('id')
                # 
                # soup = BeautifulSoup(urllib2.urlopen(post_url))
                # parsed = list(urlparse.urlparse(post_url))
                # 
                # out_folder = './'
                # 
                # for image in soup.findAll("img"):
                #    print "Image: %(src)s" % image
                #    filename = image["src"].split("/")[-1]
                #    parsed[2] = image["src"]
                #    outpath = os.path.join(out_folder, filename)
                #    try:
                #        urlretrieve(urlparse.urlunparse(parsed), outpath)
                #    except Exception, e:
                #        print e
                #===============================================================
                
                #===============================================================
                # lookup = soup.findAll('li', text='Size: ')
                # if len(lookup) > 0:
                #    image_url = lookup[0].next['href']
                #===============================================================
                
                image_name = image_url.split('/')[-1]

                folder_path = '../' + PATH_TO_RES + IMAGES + name + '/'
                file_path = folder_path + image_name
                
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    
                if not os.path.exists(file_path):
                    local_file = open(file_path, 'wb')
                    local_file.write(urllib2.urlopen(image_url).read())
                    local_file.close()
            
        except Exception, e:
            log.error(e)
            return False
        
#ImageGetter.getBijinImages('horikita_maki', 3)