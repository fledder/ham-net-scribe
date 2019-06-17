import sqlite3

#A class to handle data persistence
class Persist:
    
    #Constructor sets up a connection and checks the database structure.
    def __init__(self, path="dev.db"):
        self.path = path
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()
        
        self.stationTableCreate = 'CREATE TABLE stations (callsign string, name string, note string, ack bool, CONSTRAINT callsign_unique UNIQUE (callsign))'
        
        self.scriptTableCreate = 'CREATE TABLE scripts (name string, contents string, CONSTRAINT name_unique UNIQUE (name))'
        
        self.checkDatabaseStructure()
        
    #Check one table against its create statement
    def checkTableStructure(self, name, desiredStructure):
        self.cur.execute("SELECT sql FROM sqlite_master WHERE name = ?", (name,))
        currentTableStructure = self.cur.fetchone()
        if currentTableStructure is None or currentTableStructure[0] != desiredStructure:
            self.cur.execute("SELECT COUNT(sql) FROM sqlite_master WHERE name = ?", (name,))
            if self.cur.fetchone()[0] > 0:
                self.cur.execute("DROP TABLE "+name+";")
                self.con.commit()
            self.cur.execute(desiredStructure)
            self.con.commit()
            print('Reset table: ' + name)
        
    #Use the previous method to check all required tables
    def checkDatabaseStructure(self):
        self.checkTableStructure('stations', self.stationTableCreate)
        self.checkTableStructure('scripts', self.scriptTableCreate)
       
    def loadFromDatabase(self):
        pass