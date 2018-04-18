import mysql.connector

cnx = mysql.connector.connect(user='testUser', password='Testing123!',
                              host='127.0.0.1',
                              database='it350')


cursor = cnx.cursor()

query = "SHOW STATUS"
cursor.execute(query)
message = ""
for (Name, NUM) in cursor:
    message += ("<div>{}: {}</div>".format(
        Name, NUM))

cursor.close()
cnx.close()

import sys
