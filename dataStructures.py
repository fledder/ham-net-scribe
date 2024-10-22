PHONETIC_ALPHABET = {
    'A': 'ALPHA',
    'B': 'BRAVO',
    'C': 'CHARLIE',
    'D': 'DELTA',
    'E': 'ECHO',
    'F': 'FOXTROT',
    'G': 'GOLF',
    'H': 'HOTEL',
    'I': 'INDIA',
    'J': 'JULIET',
    'K': 'KILO',
    'L': 'LIMA',
    'M': 'MIKE',
    'N': 'NOVEMBER',
    'O': 'OSCAR',
    'P': 'PAPA',
    'Q': 'QUEBEC',
    'R': 'ROMEO',
    'S': 'SIERRA',
    'T': 'TANGO',
    'U': 'UNIFORM', #'UNICORN',
    'V': 'VICTOR',
    'W': 'WHISKEY',
    'X': 'XRAY',
    'Y': 'YANKEE',
    'Z': 'ZULU',
    '0': 'ZERO',
    '1': 'ONE',
    '2': 'TWO',
    '3': 'THREE', #'TREE',
    '4': 'FOUR', #'FOWER',
    '5': 'FIVE', #'FIFE',
    '6': 'SIX',
    '7': 'SEVEN',
    '8': 'EIGHT',
    '9': 'NINER', #'NINE'
    ' ': ''
}

#Class for a single station
class Station:
    
    #Constructor
    def __init__(self, callsign='', name='', ack=False, note='', id = None):
        self.callsign = callsign.upper()
        self.name = name
        self.ack = ack
        self.note = note
        self.id = id
        if ack:
            self.ackText = 'Yes'
        else:
            self.ackText = ''
    
    #Test a station for a callsign match
    def match(self, pattern):
        match = True
        for i in range(len(self.callsign)):
            if pattern[i] != '/' and pattern[i] != self.callsign[i]:
                match = False
        return match
    
    #Load from database, given an ID
    def loadFromDatabase(self, p):
        p.cur.execute('SELECT callsign, name, ack, note FROM stations WHERE rowid = ?', (self.id,))
        line = p.cur.fetchone()
        if len(line) > 0:
            self.callsign = line[0]
            self.name = line[1]
            self.ack = line[2]
            self.note = line[3]
        else:
            raise RuntimeError
    
    #Save to database, either update or insert
    def saveToDatabase(self, p):
        if self.id is not None:
            p.cur.execute('UPDATE stations SET callsign = ?, name = ?, ack = ?, note = ? WHERE rowid = ?;', 
                (self.callsign, self.name, self.ack, self.note, self.id))
            p.con.commit()
        else:
            p.cur.execute('INSERT INTO stations (callsign, name, ack, note) VALUES (?, ?, ?, ?);',
                (self.callsign, self.name, self.ack, self.note))
            p.con.commit()
            self.id = p.cur.lastrowid
    
    #Change the station's acknowledge status
    def toggleAck(self):
        if self.ack:
            self.ack = False
            self.ackText = ''
        else:   
            self.ack = True
            self.ackText = 'Yes'
    
    #Get an array of phonetic words from the callsign
    def getPhoneticArray(self):
        outList = []
        for callChar in self.callsign:
            outList.append(PHONETIC_ALPHABET[callChar])
        return outList

#Class for a single net script
class Script:
    
    #Constructor
    def __init__(self, name='', contents = '', id = None):
        self.name = name
        self.contents = contents
        self.id = id
    
    #Load from database, given an ID
    def loadFromDatabase(self, p):
        p.cur.execute('SELECT name, contents FROM scripts WHERE rowid = ?', (self.id,))
        line = p.cur.fetchone()
        if len(line) > 0:
            self.name = line[0]
            self.contents = line[1]
        else:
            raise RuntimeError
    
    #Save to database, either update or insert
    def saveToDatabase(self, p):
        if self.id is not None:
            p.cur.execute('UPDATE scripts SET name = ?, contents = ? WHERE rowid = ?;', (self.name, self.contents, self.id))
            p.con.commit()
        else:
            p.cur.execute('INSERT INTO scripts (name, contents) VALUES (?, ?);', (self.name, self.contents))
            p.con.commit()
            self.id = p.cur.lastrowid

#A class to handle the list of stations
class StationList:
    
    currentStation = Station()
    currentStationIndex = 0
    
    def __init__(self, p):
        self.list = []
        self.updateListFromDatabase(p)
        self.currentStationIndex = 0
        self.currentStation = self.list[self.currentStationIndex]
    
    def updateListFromDatabase(self, p):
        for row in p.cur.execute('SELECT rowid, callsign, name, ack, note FROM stations ORDER BY callsign;'):
            self.list.append(Station(row[1], row[2], row[3], row[4], row[0]))
    
    def selectNext(self):
        self.currentStationIndex = self.currentStationIndex + 1
        if self.currentStationIndex >= len(self.list):
            self.currentStationIndex = 0
        self.currentStation = self.list[self.currentStationIndex]
    
    def selectPrevious(self):
        self.currentStationIndex = self.currentStationIndex - 1
        if self.currentStationIndex < 0:
            self.currentStationIndex = len(self.list) - 1
        self.currentStation = self.list[self.currentStationIndex]
    
    def selectStation(self, index):
        if index >= 0 and index < len(self.list):
            self.currentStationIndex = index
            self.currentStation = self.list[self.currentStationIndex]