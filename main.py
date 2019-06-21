"""
    This application manages clerical functions needed by a person
    running a ham radio net, or at least the functions needed
    by the people who programmed this application. Effort has been
    made to avoid complication, so there is no provision for teams
    or geo-lookup or such things. Just a callsign, a name, an 
    acknowledged flag, and a short note. 
    
    This application also maintains a list of callsigns that have 
    been checked in before, and provides the opportunity to insert
    the call and name for that person from the list.
    
    See https://github.com/fledder/ham-net-scribe for more info
    or to contribute.
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import (Qt, pyqtSignal, QObject, QEvent)

from persist import Persist
from dataStructures import Station, Script, StationList
from customWidgets import *

p = Persist()


PHONETIC_STYLESHEET = '''
    background-color: rgb(0, 0, 0, 255);
    font-family: "Consolas";
    font-size: 24px;
    font-style: bold;
    color: rgb(128, 255, 255, 255);
    qproperty-alignment: AlignCenter;
    '''

class MainFormWidget(QWidget):
    
    """
    Class for the main window. 
    """
    
    acknowledgedToggle = pyqtSignal()
    selectRight = pyqtSignal()
    selectLeft = pyqtSignal()
    refreshSignal = pyqtSignal()
    selectNextSignal = pyqtSignal()
    selectPreviousSignal = pyqtSignal()
    cursorRight = pyqtSignal()
    cursorLeft = pyqtSignal()
    deleteSignal = pyqtSignal()
    
    '''--------------------------------------------
    Key press handling
    --------------------------------------------'''
    
    def keyPressEvent(self, event):
    
        """
        Key presses are handled by the main form. This app does not allow
        individual control focus (at least on the main window) to prevent
        delays due to trying to move around fields.
        """
        
        isLetter = event.key() >= Qt.Key_A and event.key() <= Qt.Key_Z
        isNumber = event.key() >= Qt.Key_0 and event.key() <= Qt.Key_9
        isSpace = event.key() == Qt.Key_Space
        
        #Letters, numbers, and spaces are handled by edit boxes.
        #Spaces are not valid for callsigns, and toggle acknowledgement
        #when the callsign box is selected.
        if (isLetter or isNumber) and self.callsignBox.selected:
            self.callsignBox.handleInput(event)
            self.saveCallsign()
        elif isLetter or isNumber or isSpace:
            if self.nameBox.selected:
                self.nameBox.handleInput(event)
                self.saveName()
            elif self.noteBox.selected:
                self.noteBox.handleInput(event)
                self.saveNote()

        
        else:
        #All other key presses are checked against this list of 
        #valid shortcut / control keys and mapped appropriately.
            unmodifiedKeyMap = {
                Qt.Key_Space: self.acknowledgedToggle.emit,
                Qt.Key_Right: self.cursorRight.emit,
                Qt.Key_Left: self.cursorLeft.emit,
                Qt.Key_Tab: self.selectRight.emit,
                Qt.Key_Backtab: self.selectLeft.emit,
                Qt.Key_F5: self.refreshSignal.emit,
                Qt.Key_Up: self.selectPreviousSignal.emit,
                Qt.Key_Down: self.selectNextSignal.emit,
                Qt.Key_Delete: self.deleteSignal.emit,
                }
                
            keyMap = unmodifiedKeyMap
            
            if event.key() in keyMap:
                keyMap[event.key()]()
    
    
    '''--------------------------------------------
    Assorted action functions
    --------------------------------------------'''
    
    #Function to update the phonetic boxes when the call changes
    def updatePhonetics(self):
        phoneticArray = self.stations.currentStation.getPhoneticArray()
        for i in range(6):
            self.phoneticLabels[i].setText(phoneticArray[i])
    
    #Next 3 take care of updating the current station and saving it, then
    #refreshing other widgets that may need to be refreshed.
    def saveCallsign(self):
        if self.callsignBox.selected:
            print('saving callsign')
            self.stations.currentStation.callsign = self.callsignBox.text()
            self.stations.currentStation.saveToDatabase(p)
            self.stationTable.refresh(self.stations)
            self.updatePhonetics()
    
    def saveName(self):
        if self.nameBox.selected:
            self.stations.currentStation.name = self.nameBox.text()
            self.stations.currentStation.saveToDatabase(p)
            self.stationTable.refresh(self.stations)
    
    def saveNote(self):
        if self.noteBox.selected:
            self.stations.currentStation.note = self.noteBox.text()
            self.stations.currentStation.saveToDatabase(p)
            self.stationTable.refresh(self.stations)
    
    #Refresh the widgets when the selected station changes
    def changeSelection(self):
        self.callsignBox.setText(self.stations.currentStation.callsign)
        self.nameBox.setText(self.stations.currentStation.name)
        self.noteBox.setText(self.stations.currentStation.note)
        self.setAck(self.stations.currentStation.ack)
        self.stationTable.setSelection(self.stations.currentStation.callsign)
        self.updatePhonetics()
    
    #Action helpers for advancing / retreating the selection
    def selectNext(self):
        self.stations.selectNext()
        self.changeSelection()
    
    def selectPrevious(self):
        self.stations.selectPrevious()
        self.changeSelection()
    
    #Handles the refresh of the ack state indicator
    def setAck(self, state):
        if state:
            self.ackLabel.setPixmap(self.unackPixmap)
        else:
            self.ackLabel.setPixmap(self.ackPixmap)
    
    #Update the state of the station, refresh the indicator
    def toggleAck(self):
        if self.callsignBox.selected:
            self.stations.currentStation.toggleAck()
            self.stations.currentStation.saveToDatabase(p)
            self.setAck(self.stations.currentStation.ack)
    
    #Change which editor is highlighted / selected
    def changeHighlight(self, highlightIndex):
        controls = {0: self.callsignBox, 1: self.nameBox, 2: self.noteBox}
        for key, control in controls.items():
            if key == highlightIndex:
                control.select()
            else:
                control.deselect()
    
    #Move the editor selection right
    def changeSelectionRight(self):
        self.selectedControl = self.selectedControl + 1
        if self.selectedControl > 2:
            self.selectedControl = 0
        self.changeHighlight(self.selectedControl)
    
    #Move editor selection left
    def changeSelectionLeft(self):
        self.selectedControl = self.selectedControl - 1
        if self.selectedControl < 0:
            self.selectedControl = 2
        self.changeHighlight(self.selectedControl)
    
    
    '''--------------------------------------------
    Init function, graphics creation
    --------------------------------------------'''
    
    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()
        self.selectedControl = 0
        
        '''--------------------------------------------
        Upper layout: editors and their labels
        --------------------------------------------'''
        self.upperLayout = QGridLayout()
        
        #Callsign editor uses an overridden line edit
        self.callsignLabel = QLabel('Callsign')
        self.upperLayout.addWidget(self.callsignLabel,0,0)
        self.callsignBox = callsignEdit()
        self.callsignBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.callsignBox,1,0)
        
        #Name editor uses an overridden line edit
        self.nameLabel = QLabel('Name')
        self.upperLayout.addWidget(self.nameLabel,0,1)
        self.nameBox = primaryEdit()
        self.nameBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.nameBox,1,1)
        
        #Ack indicator uses a pixmap
        self.ackLabel = QLabel('Acknowledged')
        self.upperLayout.addWidget(self.ackLabel,0,2)
        self.ackPixmap = QPixmap('green-check.png').scaled(20, 20)
        self.unackPixmap = QPixmap('red-dashed-square.png').scaled(20,20)
        self.ackLabel = QLabel()
        self.ackLabel.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.ackLabel,1,2)
        
        #Note editor uses the same overridden line edit as the name editor
        self.noteLabel = QLabel('Notes')
        self.upperLayout.addWidget(self.noteLabel,0,3)
        self.noteBox = primaryEdit()
        self.noteBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.noteBox,1,3)
        
        #Add the upper layout into the main layout now that it's complete
        self.mainLayout.addLayout(self.upperLayout)
        
        #Initial state of editor selection
        self.changeHighlight(0)
        
        '''--------------------------------------------
        Phonetic callsign helper layout
        --------------------------------------------'''
        self.phoneticLayout = QHBoxLayout()
        self.phoneticLabels = []
        for i in range(6):
            self.phoneticLabels.append(QLabel(''))
            self.phoneticLabels[i].setStyleSheet(PHONETIC_STYLESHEET)
            self.phoneticLayout.addWidget(self.phoneticLabels[i])
        self.mainLayout.addLayout(self.phoneticLayout)
        
        '''--------------------------------------------
        Set up the window and get the station list
        --------------------------------------------'''
        self.stations = StationList(p)
        self.setGeometry(300,300,800,500)
        self.setWindowTitle('Simple Net Scribe')
        
        '''--------------------------------------------
        Table to hold the list of stations, custom
        version of QTableWidget
        --------------------------------------------'''
        self.stationTable = stationTable(len(self.stations.list), 4)
        
        #Tell the station table to update its data from the
        #station list
        self.stationTable.populate(self.stations)
        #Render the selection for item 0
        self.changeSelection()
        
        '''--------------------------------------------
        Signal and slot connections
        --------------------------------------------'''
        self.acknowledgedToggle.connect(self.toggleAck)
        self.selectRight.connect(self.changeSelectionRight)
        self.selectLeft.connect(self.changeSelectionLeft)
        self.refreshSignal.connect(lambda: self.stationTable.refresh(self.stations))
        self.selectNextSignal.connect(self.selectNext)
        self.selectPreviousSignal.connect(self.selectPrevious)
        
        #Editors ignore events unless selected, so just connect
        #the common controls to all three
        self.cursorRight.connect(self.callsignBox.cursorRight)
        self.cursorRight.connect(self.nameBox.cursorRight)
        self.cursorRight.connect(self.noteBox.cursorRight)
        
        self.cursorLeft.connect(self.callsignBox.cursorLeft)
        self.cursorLeft.connect(self.nameBox.cursorLeft)
        self.cursorLeft.connect(self.noteBox.cursorLeft)
        
        #Need to come up with a way to not save everything every time...
        self.deleteSignal.connect(self.callsignBox.handleDelete)
        self.deleteSignal.connect(self.saveCallsign)
        self.deleteSignal.connect(self.nameBox.handleDelete)
        self.deleteSignal.connect(self.saveName)
        self.deleteSignal.connect(self.noteBox.handleDelete)
        self.deleteSignal.connect(self.saveNote)
        
        '''--------------------------------------------
        Final layout additions
        --------------------------------------------'''
        self.mainLayout.addWidget(self.stationTable)
        self.setLayout(self.mainLayout)
        self.show()



if __name__ == '__main__':
    print('here')
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainFormWidget()
    sys.exit(app.exec_())