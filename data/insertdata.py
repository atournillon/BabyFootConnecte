import sqlite3 as lite
import time
import sys
conn = lite.connect('data/baby_foot.db')
curs=conn.cursor()

with conn:
    curs.execute("DROP TABLE IF EXISTS LIVE_MATCH")
    curs.execute("CREATE TABLE LIVE_MATCH (time_stamp DATETIME, team_1 NUMERIC, team_2 Numeric)")

# function to insert data on a table
def add_data (team_1, team_2):
    curs.execute("INSERT INTO LIVE_MATCH values(datetime('now'), (?), (?))", (team_1, team_2))
    conn.commit()

# call the function to insert data

for i in range(10):
    if i%2 == 0:
        add_data(i/2,i/2)
    else:
        add_data(i/2+1,i/2)
    time.sleep(2)

# print database content
print ("\nEntire database contents:\n")
for row in curs.execute("SELECT * FROM LIVE_MATCH"):
    print (row)

# close the database after use
conn.close()
