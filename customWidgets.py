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
    
    def isValidCall(self):
        import re
        if re.match(r'[a-zA-Z]{1,2}\d[a-zA-Z]{1,3}', self.text()):
            return True
        return False
    
    def handleInput(self, key):
        pass
    
    def paintEvent(self, event):
    
        import re
        
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        
        if self.isValidCall():
            callToDisplay = self.text()
        else:
            parts = re.search(r"([a-zA-Z\{1,2})(\d)([a-zA-Z]{1,3})", self.text())
            if len(parts.groups()) >= 3:
                prefix = parts.group(0)
                number = parts.group(1)
                suffix = parts.group(2)
            else:
                numberMatch = re.search(r"\d", self.text())
                if numberMatch:
                    prefix = self.text()[0:numberMatch.start()]
                    number = self.text()[numberMatch.start(): numberMatch.start() + 1]
                    suffix = self.text()[numberMatch.start()+1:]
                    if len(prefix) == 0:
                        prefix = '  '
                    if len(suffix) == 0:
                        suffix = '   '
                else:
                    number = '#'
                    if len(self.text()) >= 3:
                        prefix = self.text()[:2]
                        suffix = self.text()[2:]
                    elif len(self.text()) == 2:
                        prefix = self.text()
                        suffix = '   '
                    elif len(self.text()) == 1:
                        prefix = self.text()
                        suffix = '   '
                    else:
                        prefix = '  '
                        suffix = '   '
                
            callToDisplay = prefix + number + suffix
            
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
        textBottom = int(textHeight * .85)
        
        
        charRectBrush = QBrush(Qt.SolidPattern)
        charRectBrush.setColor(self.palette().color(QWidget.backgroundRole(self)).darker(130))
        for offset in range(6):
            rectLeft = textLeft + fontMetrics.width(' '*callOffset + callToDisplay[:(offset - callOffset)]) + 1
            rectTop = textHeight * .2
            rectWidth = fontMetrics.width(' ') - 2
            rectHeight = fontMetrics.height() * .8
            painter.fillRect(rectLeft, rectTop, rectWidth, rectHeight, charRectBrush)
        
        painter.drawText(textLeft, textBottom, callToDisplay)
        
        cursorLeft = textLeft + fontMetrics.width(callToDisplay[:self.cursorPos])
        cursorWidth = fontMetrics.width(callToDisplay[self.cursorPos])
        
        cursorBrush = QBrush(Qt.SolidPattern)
        cursorBrush.setColor(QColor(0, 0, 0, 255))
        cursor = painter.drawRect(cursorLeft, textHeight, cursorWidth, 3)
        painter.fillRect(cursorLeft, textHeight, cursorWidth, 3, cursorBrush)
        