from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import (Qt, pyqtSignal, QObject, QEvent, Qt)

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
    
    def refresh(self, stations):
        for i in range(len(stations.list)):
            station = stations.list[i]
            if self.item(i, 0).text() != station.callsign:
                print('Changing callsign at ' + str(i))
                self.setItem(i, 0, QTableWidgetItem(station.callsign))
                
            if self.item(i, 1).text() != station.name:
                print('Changing name at ' + str(i))
                self.setItem(i, 1, QTableWidgetItem(station.name))
                
            if self.item(i, 2).text() != station.ackText:
                print('Changing ack at ' + str(i))
                self.setItem(i, 2, QTableWidgetItem(station.ackText))
                
            if self.item(i, 3).text() != station.note:
                print('Changing note at ' + str(i))
                self.setItem(i, 3, QTableWidgetItem(station.note))
    
    def setSelection(self, callsign):
        for i in range(self.rowCount()):
            if self.item(i, 0).text() == callsign:
                self.setCurrentItem(self.item(i, 0))

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
    
    def handleInput(self, event):
        if self.selected:
            pressedChar = event.text().upper()
            print(self.cursorPos)
            if pressedChar in '0123456789':
                self.cursorPos = 3
                self.setText(self.text()[:2]+pressedChar+self.text()[3:])
            else:
                if self.cursorPos == 0 and pressedChar not in 'KNW':
                    self.cursorPos = 1
                if self.cursorPos == 2:
                    self.cursorPos = 3
                if self.cursorPos < len(self.text()):
                    self.setText(self.text()[:self.cursorPos] + pressedChar + self.text()[self.cursorPos+1:])
                else:
                    self.setText(self.text()[:self.cursorPos] + pressedChar)
                self.cursorRight()
            self.repaint()
    
    def handleDelete(self):
        if self.selected:
            if self.cursorPos == 0:
                self.setText(' '+self.text()[1:])
                self.cursorRight()
            elif self.cursorPos == 1:
                self.setText(' '+self.text()[0]+self.text()[2:])
                self.cursorRight()
            elif self.cursorPos == 2:
                self.setText(self.text()[:2] + ' ' + self.text()[3:])
                self.cursorRight()
            else:
                self.setText(self.text()[:3]+self.text()[4:]+' ')
                self.repaint()
    
    def paintEvent(self, event):
    
        import re
        
        if self.selected:
            self.setStyleSheet(EDITOR_SELECTED_STYLESHEET)
        else:
            self.setStyleSheet(EDITOR_UNSELECTED_STYLESHEET)
        
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        
        
        callToDisplay = self.text()
            
        fontMetrics = self.fontMetrics()
        textWidth = fontMetrics.width(callToDisplay)
        textHeight = fontMetrics.height()
        
        totalCallWidth = fontMetrics.width('XX#XXX')
        
        digitMatch = re.search(r"[0-9]", callToDisplay)
        if digitMatch:
            digitIndex = digitMatch.start()
            if digitIndex < 3:
                callOffset = 2 - digitIndex
            else:
                callOffset = 0
        else:
            callOffset = 0
        
        callOffsetDistance = fontMetrics.width('0'*callOffset)
        
        
        textLeft = ((self.width() - totalCallWidth) / 2) + callOffsetDistance
        textBottom = int(textHeight * .9)
        
        
        charRectBrush = QBrush(Qt.SolidPattern)
        charRectBrush.setColor(self.palette().color(QWidget.backgroundRole(self)).darker(125))
        for offset in range(len(callToDisplay)):
            thisChar = callToDisplay[offset]
            rectLeft = textLeft + fontMetrics.width(callToDisplay[:(offset)])
            rectTop = textBottom * .25
            rectWidth = fontMetrics.width(thisChar) - 2
            rectHeight = fontMetrics.height() * .8
            painter.fillRect(rectLeft, rectTop, rectWidth, rectHeight, charRectBrush)
        
        painter.drawText(textLeft, textBottom, callToDisplay)
        
        if self.selected:
            cursorLeft = textLeft + fontMetrics.width(callToDisplay[:self.cursorPos])
            cursorWidth = fontMetrics.width(callToDisplay[self.cursorPos])
            
            cursorBrush = QBrush(Qt.SolidPattern)
            cursorBrush.setColor(QColor(0, 0, 0, 255))
            cursor = painter.drawRect(cursorLeft, textHeight, cursorWidth, 3)
            painter.fillRect(cursorLeft, textHeight, cursorWidth, 3, cursorBrush)
        
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
    
    def handleInput(self, event):
        if self.selected:
            pressedChar = event.text().upper()
            if self.cursorPos < len(self.text()):
                self.setText(self.text()[:self.cursorPos] + pressedChar + self.text()[self.cursorPos:])
            else:
                self.setText(self.text()[:self.cursorPos] + pressedChar)
            self.cursorRight()
    
    def handleDelete(self):
        if self.selected:
            self.setText(self.text()[:self.cursorPos]+self.text()[self.cursorPos+1:])
            self.repaint()
    
    def paintEvent(self, event):
    
        if self.selected:
            self.setStyleSheet(EDITOR_SELECTED_STYLESHEET)
        else:
            self.setStyleSheet(EDITOR_UNSELECTED_STYLESHEET)
        
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        
        fontMetrics = self.fontMetrics()
        textWidth = fontMetrics.width(self.text())
        textHeight = fontMetrics.height()
        
        textLeft = ((self.width() - textWidth) / 2)
        textBottom = int(textHeight * .9)
        
        painter.drawText(textLeft, textBottom, self.text())
        
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