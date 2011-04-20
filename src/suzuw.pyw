# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2011

@author: Yadavito
'''

import suzu
from jdict.db import redict		#oh, well
import ctypes

#company.product.subproduct.version
appid = 'nonebyte.suzu.suzu.001'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

suzu.main()