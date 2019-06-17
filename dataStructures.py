#Class for a single station
class Station:
    
    #Constructor
    def __init__(self, callsign='', name='', ack=False, note='', id = None):
        self.callsign = callsign.upper()
        self.name = name
        self.ack = ack
        self.note = note
        self.id = id
    
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

class StationList:
    
    currentStation = Station()
    
    def __init__(self, p):
        self.list = []
        self.updateListFromDatabase(p)
    
    def updateListFromDatabase(self, p):
        for row in p.cur.execute('SELECT rowid, callsign, name, ack, note FROM stations ORDER BY callsign;'):
            self.list.append(Station(row[1], row[2], row[3], row[4], row[0]))
    
    