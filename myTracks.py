import sqlite3
import xml.etree.ElementTree as ET

conn = sqlite3.connect('trackdb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS Genre;

CREATE TABLE Artist (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Album (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id INTEGER,
    title TEXT UNIQUE
);

CREATE TABLE Track (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title TEXT UNIQUE,
    album_id INTEGER,
    genre_id  INTEGER,
    len INTEGER, rating INTEGER, count INTEGER
);
''')

fname = raw_input('Enter file name: ')
if ( len(fname) < 1 ) : fname = 'Library.xml'

# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>

# Function - Enter the data in to Dictionary
def myLookup(dict,d):
    found = False
    for child in d:
        if found : 
            dict[myKey]=child.text
            found = False
        if child.text in dict :
            myKey=child.text
            found = True
# Function - check the Track ID
def check(d):
    for child in d:
        if child.text=='Track ID': return True
        print child.text
    return False

stuff = ET.parse(fname)
all = stuff.findall('dict/dict/dict')
print 'Dict count:', len(all)
aa=0
for entry in all:
    dict={'Name':None,'Artist':None,'Album':None,'Play Count':None,'Rating':None,'Total Time':None,'Genre':None}
    if not check(entry) : continue    
    myLookup(dict,entry)

    
    if dict['Name'] is None or dict['Artist'] is None or dict['Album'] is None or dict['Genre'] is None: 
        continue

    print dict['Name'], dict['Artist'], dict['Album'], dict['Play Count'], dict['Rating'], dict['Total Time'], dict['Genre']

    cur.execute('''INSERT OR IGNORE INTO Artist (name) 
        VALUES ( ? )''', ( dict['Artist'], ) )
    cur.execute('SELECT id FROM Artist WHERE name = ? ', (dict['Artist'], ))
    artist_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR IGNORE INTO Genre (name) 
        VALUES ( ? )''', ( dict['Genre'], ) )
    cur.execute('SELECT id FROM Genre WHERE name = ? ', (dict['Genre'], ))
    genre_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) 
        VALUES ( ?, ? )''', ( dict['Album'], artist_id ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (dict['Album'], ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, genre_id, len, rating, count) 
        VALUES ( ?, ?, ?, ?, ?, ? )''', 
        ( dict['Name'], album_id, genre_id, dict['Total Time'], dict['Rating'], dict['Play Count'] ) )
    conn.commit()
