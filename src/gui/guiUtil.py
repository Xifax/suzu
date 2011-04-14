# -*- coding: utf-8 -*-
'''
Created on Mar 2, 2011

@author: Yadavito
'''

# external #
from PySide.QtCore import QRect, QSize, QObject, QEvent, Signal
from PySide.QtGui import QRegion

def roundCorners(rectangle, radius):
        '''Get region for setting round edges mask'''
        region = QRegion()
        region += rectangle.adjusted(radius,0,-radius,0)
        region += rectangle.adjusted(0,radius,-0,-radius)
        
        corner = QRect(rectangle.topLeft(), QSize(radius*2,radius*2))
        region += QRegion(corner, QRegion.Ellipse)
        
        corner.moveTopRight(rectangle.topRight())
        region += QRegion(corner, QRegion.Ellipse)
        
        corner.moveBottomLeft(rectangle.bottomLeft())
        region += QRegion(corner, QRegion.Ellipse)
        
        corner.moveBottomRight(rectangle.bottomRight())
        region += QRegion(corner, QRegion.Ellipse)
        
        return region
    
def unfillLayout(layoutName):
    '''Empty layout from widgets (should be reinit'd, if in another layout)'''
    def deleteItems(layout): 
        if layout is not None: 
            while layout.count(): 
                item = layout.takeAt(0) 
                widget = item.widget() 
                if widget is not None: 
                    widget.deleteLater() 
                else: 
                    deleteItems(item.layout()) 
    deleteItems(layoutName) 
    
def clickable(widget):
    '''Add clicked event to widget'''
    class Filter(QObject):
    
        clicked = Signal()
        
        def eventFilter(self, obj, event):
        
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    self.clicked.emit()
                    return True
            
            return False
    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked