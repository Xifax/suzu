'''
Created on Mar 17, 2011

@author: Yadavito
'''

import logging

log = logging.getLogger('log')
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)-24s %(threadName)-11s %(levelname)-10s %(message)s')

filehandler = logging.FileHandler('suzu.log', 'a')
filehandler.setLevel(logging.DEBUG)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)