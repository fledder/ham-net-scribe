"""
This module defines custom widgets used in the main program.
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import (Qt, pyqtSignal, QObject, QEvent, Qt)

'''--------------------------------------------
Some configuration variables
--------------------------------------------'''

TABLE_STYLESHEET = '''
    background-color: rgb(32, 32, 32, 255);
    color: rgb(255, 255, 255, 255);
    selection-background-color: rgb(200, 200, 200, 255);
    selection-color: rgb(0, 0, 0, 255);
    font-family: "consolas";
    font-size: 18px;
    '''

EDITOR_COMMON_STYLESHEET = '''
    font-family: "Consolas";
    font-size: 24px;
    font-style: bold;
    '''

EDITOR_SELECTED_STYLESHEET = '''
    background-color: rgb(200, 255, 200, 255);
    border: 4px solid green;
    color: rgb(0, 0, 0, 255);
    ''' + EDITOR_COMMON_STYLESHEET

EDITOR_UNSELECTED_STYLESHEET = '''
    background-color: rgb(127, 127, 127, 255);
    border: 4px solid gray;
    color: rgb(255, 255, 255, 255);
    ''' + EDITOR_COMMON_STYLESHEET


class stationTable(QTableWidget):
    '''--------------------------------------------
    A table for the data to display, with various
    helper methods.
    --------------------------------------------'''
    
    def __init__(self, one, two):
        QTableWidget.__init__(self, one, two)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.setStyleSheet(TABLE_STYLESHEET)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.setFocusPolicy(Qt.NoFocus)
    
    '''--------------------------------------------
    Use the station list to create the items in the
    table
    --------------------------------------------'''
    def populate(self, stations):
        for i in range(len(stations.list)):
            station = stations.list[i]
            itemToInsert = QTableWidgetItem(station.callsign)
            self.setItem(i, 0, itemToInsert)
            itemToInsert = QTableWidgetItem(station.name)
            self.setItem(i, 1, itemToInsert)
            itemToInsert = QTableWidgetItem(station.ackText)
            self.setItem(i, 2, itemToInsert)
            itemToInsert = QTableWidgetItem(station.note)
            self.setItem(i, 3, itemToInsert)
    
    '''--------------------------------------------
    Assuming the number of stations hasn't changed,
    update the data for each
    --------------------------------------------'''
    def refresh(self, stations):
        for i in range(len(stations.list)):
            station = stations.list[i]
            if self.item(i, 0).text() != station.callsign:
                self.setItem(i, 0, QTableWidgetItem(station.callsign))
                
            if self.item(i, 1).text() != station.name:
                self.setItem(i, 1, QTableWidgetItem(station.name))
                
            if self.item(i, 2).text() != station.ackText:
                self.setItem(i, 2, QTableWidgetItem(station.ackText))
                
            if self.item(i, 3).text() != station.note:
                self.setItem(i, 3, QTableWidgetItem(station.note))
    '''--------------------------------------------
    Set the current selection based on a callsign
    --------------------------------------------'''
    def setSelection(self, callsign):
        for i in range(self.rowCount()):
            if self.item(i, 0).text() == callsign:
                self.setCurrentItem(self.item(i, 0))

'''--------------------------------------------
Custom subclass of QLineEdit with validation
and methods for callsign display. Uses events
for typing rather than focus to enable it to 
work while not focused.
--------------------------------------------'''
class callsignEdit(QLineEdit):
    
    selected = True
    cursorPos = 0
    
    def __init__(self):
        QLineEdit.__init__(self)
    
    def select(self):
        self.selected = True
        self.repaint()
    
    def deselect(self):
        self.selected = False
        self.repaint()
    
    def isValidCall(self):
        import re
        if re.match(r'[a-zA-Z]{1,2}\d[a-zA-Z]{1,3}', self.text()):
            return True
        return False
    
    #Handle text inputs
    def handleInput(self, event):
        if self.selected:
            pressedChar = event.text().upper()
            #If it's a number, it goes in the number location in the call
            if pressedChar in '0123456789':
                self.cursorPos = 3
                self.setText(self.text()[:2]+pressedChar+self.text()[3:])
            #If it's a letter:
            else:
                #US calls only at the moment, so anything besides K N or W
                #cannot be the first letter
                if self.cursorPos == 0 and pressedChar not in 'KNW':
                    self.cursorPos = 1
                #If the cursor is in the number location, skip to the next
                #letter location
                if self.cursorPos == 2:
                    self.cursorPos = 3
                #If the cursor is in the middle of the word, insert the character
                if self.cursorPos < len(self.text()):
                    self.setText(self.text()[:self.cursorPos] + pressedChar + self.text()[self.cursorPos+1:])
                #Otherwise, insert at the end
                else:
                    self.setText(self.text()[:self.cursorPos] + pressedChar)
                #After typing letters, advance the cursor
                self.cursorRight()
            #Must call repaint manually
            self.repaint()
    
    #Handle the delete key
    def handleDelete(self):
        if self.selected:
            #These conditionals make sure the call stays justified at the number
            #First position, insert a space instead and advance the cursor
            if self.cursorPos == 0:
                self.setText(' '+self.text()[1:])
                self.cursorRight()
            #Second position, move the first character over
            elif self.cursorPos == 1:
                self.setText(' '+self.text()[0]+self.text()[2:])
                self.cursorRight()
            #Number position, just replace the number with a space
            elif self.cursorPos == 2:
                self.setText(self.text()[:2] + ' ' + self.text()[3:])
                self.cursorRight()
            #Suffix, move everythig left and replace with spaces
            else:
                self.setText(self.text()[:3]+self.text()[4:]+' ')
                self.repaint()
    
    #Customized paint method
    def paintEvent(self, event):
    
        import re
        
        #Set the stylesheet based on whether or not it's selected
        if self.selected:
            self.setStyleSheet(EDITOR_SELECTED_STYLESHEET)
        else:
            self.setStyleSheet(EDITOR_UNSELECTED_STYLESHEET)
        
        #This chunk forces the control to obey the stylesheet
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        
        #had some code to justify the call, but now the database
        #uses spaces to justify it in the record so just use
        #the current text
        callToDisplay = self.text()
        
        #get some info about the size of the text
        fontMetrics = self.fontMetrics()
        textWidth = fontMetrics.width(callToDisplay)
        textHeight = fontMetrics.height()
        
        #get position for centering text
        textLeft = ((self.width() - textWidth) / 2)
        #I don't know how this works, but this looks OK and I don't
        #have time to research it at the moment
        textBottom = int(textHeight * .9)
        
        #Get a brush that's a little bit darker than the current background color
        charRectBrush = QBrush(Qt.SolidPattern)
        charRectBrush.setColor(self.palette().color(QWidget.backgroundRole(self)).darker(125))
        #Loop through the number of characters and print boxes behind them
        for offset in range(len(callToDisplay)):
            thisChar = callToDisplay[offset]
            rectLeft = textLeft + fontMetrics.width(callToDisplay[:(offset)])
            rectTop = textBottom * .25
            rectWidth = fontMetrics.width(thisChar) - 2
            rectHeight = fontMetrics.height() * .8
            painter.fillRect(rectLeft, rectTop, rectWidth, rectHeight, charRectBrush)
        
        #Draw the text
        painter.drawText(textLeft, textBottom, callToDisplay)
        
        #Only draw the cursor if the control is selected
        if self.selected:
            cursorLeft = textLeft + fontMetrics.width(callToDisplay[:self.cursorPos])
            cursorWidth = fontMetrics.width(callToDisplay[self.cursorPos])
            
            cursorBrush = QBrush(Qt.SolidPattern)
            cursorBrush.setColor(QColor(0, 0, 0, 255))
            painter.fillRect(cursorLeft, textHeight, cursorWidth, 3, cursorBrush)
    
    #helper methods for moving the cursor around
    def cursorRight(self):
        self.cursorPos = self.cursorPos + 1
        if self.cursorPos > 5:
            self.cursorPos = 0
        self.repaint()
    
    def cursorLeft(self):
        self.cursorPos = self.cursorPos - 1
        if self.cursorPos < 0:
            self.cursorPos = 5
        self.repaint()

'''--------------------------------------------
Custom subclass of QLineEdit for primary data
about a station besides the callsign. Uses 
events for typing rather than focus to enable 
it to work while not focused.
--------------------------------------------'''
class primaryEdit(QLineEdit):
    
    selected = False
    cursorPos = 0
    
    def __init__(self):
        QLineEdit.__init__(self)
    
    def select(self):
        self.selected = True
        self.repaint()
    
    def deselect(self):
        self.selected = False
        self.repaint()
    
    #Handle keys input. Insert if cursor not at end.
    def handleInput(self, event):
        if self.selected:
            pressedChar = event.text().upper()
            if self.cursorPos < len(self.text()):
                self.setText(self.text()[:self.cursorPos] + pressedChar + self.text()[self.cursorPos:])
            else:
                self.setText(self.text()[:self.cursorPos] + pressedChar)
            self.cursorRight()
    
    #Handle the delete key.
    def handleDelete(self):
        if self.selected:
            self.setText(self.text()[:self.cursorPos]+self.text()[self.cursorPos+1:])
            self.repaint()
    
    #Custom paint method
    def paintEvent(self, event):
        
        #Set the correct stylesheet
        if self.selected:
            self.setStyleSheet(EDITOR_SELECTED_STYLESHEET)
        else:
            self.setStyleSheet(EDITOR_UNSELECTED_STYLESHEET)
        
        #Force it to use the stylesheet
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        
        #Get some info on the text size
        fontMetrics = self.fontMetrics()
        textWidth = fontMetrics.width(self.text())
        textHeight = fontMetrics.height()
        
        #Calculate the text position. 
        textLeft = ((self.width() - textWidth) / 2)
        textBottom = int(textHeight * .9)
        
        #Draw the text
        painter.drawText(textLeft, textBottom, self.text())
        
        #Only draw the cursor if selected
        if self.selected:
            cursorLeft = textLeft + fontMetrics.width(self.text()[:self.cursorPos])
            if self.cursorPos < len(self.text()):
                cursorWidth = fontMetrics.width(self.text()[self.cursorPos])
            else:
                cursorWidth = fontMetrics.width('0')
            
            cursorBrush = QBrush(Qt.SolidPattern)
            cursorBrush.setColor(QColor(0, 0, 0, 255))
            cursor = painter.drawRect(cursorLeft, textHeight, cursorWidth, 3)
            painter.fillRect(cursorLeft, textHeight, cursorWidth, 3, cursorBrush)
    #Helpers to move the cursor around
    def cursorRight(self):
        self.cursorPos = self.cursorPos + 1
        if self.cursorPos > len(self.text()):
            self.cursorPos = 0
        if len(self.text()) == 0:
            self.cursorPos = 0
        self.repaint()
    
    def cursorLeft(self):
        self.cursorPos = self.cursorPos - 1
        if self.cursorPos < 0:
            self.cursorPos = len(self.text())
        if len(self.text()) == 0:
            self.cursorPos = 0
        self.repaint()