# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2011

@author: Yadavito
'''

# own #
import suzu
from jdict.db import redict		#oh, well
from settings.constants import __version__, __application__

# internal #
import ctypes

#company.product.subproduct.version
id = '.'.join(['nonebyte', __application__, __application__, __version__.replace('.', '')])
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id)

suzu.main()