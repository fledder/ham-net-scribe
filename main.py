from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import (Qt, pyqtSignal, QObject, QEvent)

from persist import Persist
from dataStructures import Station, Script, StationList

p = Persist()

class stationTable(QTableWidget):
    
    tableSelectionChanged = pyqtSignal()
    acknowledgedToggle = pyqtSignal()
    
    def __init__(self, one, two):
        QTableWidget.__init__(self, one, two)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def populate(self, stations):
        for i in range(len(stations.list)):
            station = stations.list[i]
            itemToInsert = QTableWidgetItem(station.callsign)
            self.setItem(i, 0, itemToInsert)
            itemToInsert = QTableWidgetItem(station.name)
            self.setItem(i, 1, itemToInsert)
            itemToInsert = QTableWidgetItem(station.ack)
            self.setItem(i, 2, itemToInsert)
            itemToInsert = QTableWidgetItem(station.note)
            self.setItem(i, 3, itemToInsert)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if len(self.selectedItems()) >= 1:
                nextIndex = self.selectedItems()[0].row()-1
            else:
                nextIndex = 0
            if nextIndex < 0:
                nextIndex = 0
            self.setCurrentItem(self.item(nextIndex,0))
            self.tableSelectionChanged.emit()
            
        elif event.key() == Qt.Key_Down:
            if len(self.selectedItems()) >= 1:
                nextIndex = self.selectedItems()[0].row()+1
            else:
                nextIndex = 0
            if nextIndex >= self.rowCount():
                nextIndex = self.rowCount() - 1
            self.setCurrentItem(self.item(nextIndex,0))
            self.tableSelectionChanged.emit()
        
        elif event.key() == Qt.Key_Space:
            self.acknowledgedToggle.emit()


class MainFormWidget(QWidget):
    
    def changeSelection(self):
        if len(self.stationTable.selectedItems()) > 0:
            selectedItem = self.stationTable.selectedItems()
            self.callsignBox.setText(selectedItem[0].text())
            self.nameBox.setText(selectedItem[1].text())
            self.noteBox.setText(selectedItem[3].text())
    
    def toggleAck(self):
        if len(self.stationTable.selectedItems()) > 0:
            selectedItem = self.stationTable.selectedItems()
            if self.ackCheckbox.isChecked():
                self.ackCheckbox.setCheckState(Qt.Unchecked)
            else:
                self.ackCheckbox.setCheckState(Qt.Checked)
    
    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()
        
        self.upperLayout = QGridLayout()
        
        self.callsignLabel = QLabel('Callsign')
        self.upperLayout.addWidget(self.callsignLabel,0,0)
        self.callsignBox = QLineEdit()
        self.callsignBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.callsignBox,1,0)
        
        self.nameLabel = QLabel('Name')
        self.upperLayout.addWidget(self.nameLabel,0,1)
        self.nameBox = QLineEdit()
        self.nameBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.nameBox,1,1)
        
        self.ackLabel = QLabel('Acknowledged')
        self.upperLayout.addWidget(self.ackLabel,0,2)
        self.ackCheckbox = QCheckBox()
        self.ackCheckbox.setFocusPolicy(Qt.NoFocus)
        self.ackCheckbox.setStyleSheet('margin-left: 50%; margin-right: 50%;')
        self.upperLayout.addWidget(self.ackCheckbox,1,2)
        
        self.noteLabel = QLabel('Notes')
        self.upperLayout.addWidget(self.noteLabel,0,3)
        self.noteBox = QLineEdit()
        self.noteBox.setFocusPolicy(Qt.NoFocus)
        self.upperLayout.addWidget(self.noteBox,1,3)
        
        self.mainLayout.addLayout(self.upperLayout)
        
        stations = StationList(p)
        self.setGeometry(300,300,800,500)
        self.setWindowTitle('Simple Net Scribe')
        self.stationTable = stationTable(len(stations.list), 4)
        
        self.stationTable.populate(stations)
        self.stationTable.tableSelectionChanged.connect(self.changeSelection)
        self.stationTable.acknowledgedToggle.connect(self.toggleAck)
        
        self.mainLayout.addWidget(self.stationTable)
        self.setLayout(self.mainLayout)
        self.show()



if __name__ == '__main__':
    print('here')
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainFormWidget()
    sys.exit(app.exec_())