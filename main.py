from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import (Qt, pyqtSignal, QObject, QEvent)

from persist import Persist
from dataStructures import Station, Script, StationList
from customWidgets import *

p = Persist()

LINEEDIT_COMMON_STYLESHEET = '''
    font-family: "Consolas";
    font-size: 24px;
    font-style: bold;
    '''

LINEEDIT_SELECTED_STYLESHEET = '''
    background-color: rgb(200, 255, 200, 255);
    border: 4px solid green;
    color: rgb(0, 0, 0, 255);
    ''' + LINEEDIT_COMMON_STYLESHEET

LINEEDIT_UNSELECTED_STYLESHEET = '''
    background-color: rgb(127, 127, 127, 255);
    border: 4px solid gray;
    color: rgb(255, 255, 255, 255);
    ''' + LINEEDIT_COMMON_STYLESHEET

class MainFormWidget(QWidget):
    
    acknowledgedToggle = pyqtSignal()
    selectRight = pyqtSignal()
    selectLeft = pyqtSignal()
    refreshSignal = pyqtSignal()
    selectNextSignal = pyqtSignal()
    selectPreviousSignal = pyqtSignal()
    cursorRight = pyqtSignal()
    cursorLeft = pyqtSignal()
    
    def keyPressEvent(self, event):
        
        isLetter = event.key() >= Qt.Key_A and event.key() <= Qt.Key_Z
        isNumber = event.key() >= Qt.Key_0 and event.key() <= Qt.Key_9
        
        if isLetter or isNumber:
            self.callsignBox.handleInput(event.key())
        
        else:
            
            unmodifiedKeyMap = {
                Qt.Key_Space: self.acknowledgedToggle.emit,
                Qt.Key_Right: self.cursorRight.emit,
                Qt.Key_Left: self.cursorLeft.emit,
                Qt.Key_Tab: self.selectRight.emit,
                Qt.Key_Backtab: self.selectLeft.emit,
                Qt.Key_F5: self.refreshSignal.emit,
                Qt.Key_Up: self.selectPreviousSignal.emit,
                Qt.Key_Down: self.selectNextSignal.emit,
                }
                
            keyMap = unmodifiedKeyMap
            
            if event.key() in keyMap:
                keyMap[event.key()]()
    
    def changeSelection(self):
        self.callsignBox.setText(self.stations.currentStation.callsign)
        self.nameBox.setText(self.stations.currentStation.name)
        self.noteBox.setText(self.stations.currentStation.note)
        self.setAck(self.stations.currentStation.ack)
        self.stationTable.setSelection(self.stations.currentStation.callsign)
    
    def selectNext(self):
        self.stations.selectNext()
        self.changeSelection()
    
    def selectPrevious(self):
        self.stations.selectPrevious()
        self.changeSelection()
    
    def setAck(self, state):
        if state:
            self.ackLabel.setPixmap(self.unackPixmap)
        else:
            self.ackLabel.setPixmap(self.ackPixmap)
    
    def toggleAck(self):
        self.stations.currentStation.toggleAck()
        self.stations.currentStation.saveToDatabase(p)
        self.setAck(self.stations.currentStation.ack)
        
    def changeHighlight(self, highlightIndex):
        controls = {0: self.callsignBox, 1: self.nameBox, 2: self.noteBox}
        for key, control in controls.items():
            if key == highlightIndex:
                control.setStyleSheet(LINEEDIT_SELECTED_STYLESHEET)
            else:
                control.setStyleSheet(LINEEDIT_UNSELECTED_STYLESHEET)
    
    def changeSelectionRight(self):
        self.selectedControl = self.selectedControl + 1
        if self.selectedControl > 2:
            self.selectedControl = 0
        self.changeHighlight(self.selectedControl)
    
    def changeSelectionLeft(self):
        self.selectedControl = self.selectedControl - 1
        if self.selectedControl < 0:
            self.selectedControl = 2
        self.changeHighlight(self.selectedControl)
    
    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()
        
        self.upperLayout = QGridLayout()
        
        self.selectedControl = 0
        
        self.callsignLabel = QLabel('Callsign')
        self.upperLayout.addWidget(self.callsignLabel,0,0)
        self.callsignBox = callsignEdit()
        self.callsignBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.callsignBox,1,0)
        
        self.nameLabel = QLabel('Name')
        self.upperLayout.addWidget(self.nameLabel,0,1)
        self.nameBox = QLineEdit()
        self.nameBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.nameBox,1,1)
        
        self.ackLabel = QLabel('Acknowledged')
        self.upperLayout.addWidget(self.ackLabel,0,2)
        self.ackPixmap = QPixmap('green-check.png').scaled(20, 20)
        self.unackPixmap = QPixmap('red-dashed-square.png').scaled(20,20)
        self.ackLabel = QLabel()
        self.ackLabel.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.ackLabel,1,2)
        
        self.noteLabel = QLabel('Notes')
        self.upperLayout.addWidget(self.noteLabel,0,3)
        self.noteBox = QLineEdit()
        self.noteBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.noteBox,1,3)
        
        self.mainLayout.addLayout(self.upperLayout)
        
        self.changeHighlight(0)
        
        self.stations = StationList(p)
        self.setGeometry(300,300,800,500)
        self.setWindowTitle('Simple Net Scribe')
        self.stationTable = stationTable(len(self.stations.list), 4)
        
        self.stationTable.populate(self.stations)
        self.changeSelection()
        
        self.acknowledgedToggle.connect(self.toggleAck)
        self.selectRight.connect(self.changeSelectionRight)
        self.selectLeft.connect(self.changeSelectionLeft)
        self.refreshSignal.connect(lambda: self.stationTable.refresh(self.stations))
        self.selectNextSignal.connect(self.selectNext)
        self.selectPreviousSignal.connect(self.selectPrevious)
        
        self.mainLayout.addWidget(self.stationTable)
        self.setLayout(self.mainLayout)
        self.show()



if __name__ == '__main__':
    print('here')
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainFormWidget()
    sys.exit(app.exec_())