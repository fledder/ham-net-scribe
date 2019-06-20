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
    
    acknowledgedToggle = pyqtSignal()
    selectRight = pyqtSignal()
    selectLeft = pyqtSignal()
    refreshSignal = pyqtSignal()
    selectNextSignal = pyqtSignal()
    selectPreviousSignal = pyqtSignal()
    
    def __init__(self, one, two):
        QTableWidget.__init__(self, one, two)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.setStyleSheet(TABLE_STYLESHEET)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
    
    def keyPressEvent(self, event):
        
        unmodifiedKeyMap = {
            Qt.Key_Space: self.acknowledgedToggle.emit,
            Qt.Key_Right: self.selectRight.emit,
            Qt.Key_Left: self.selectLeft.emit,
            Qt.Key_Tab: self.selectRight.emit,
            Qt.Key_F5: self.refreshSignal.emit,
            Qt.Key_Up: self.selectPreviousSignal.emit,
            Qt.Key_Down: self.selectNextSignal.emit,
            }
            
        shiftKeyMap = {
            Qt.Key_Backtab: self.selectLeft.emit,
        }
        
        keyMap = {}
        
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            keyMap = shiftKeyMap
        else:
            keyMap = unmodifiedKeyMap
        if event.key() in keyMap:
            keyMap[event.key()]()
        
            
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