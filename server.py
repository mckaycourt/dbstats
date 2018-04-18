# !/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer

from datetime import datetime
import mysql.connector
from urllib.parse import urlparse

import os

import backup
from pymongo import MongoClient

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        query = urlparse(self.path).query
        path = self.path.split('?')

        self.send_response(200)

        # Send headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if path[0] == '/api/login':
            try:
                query_components = dict(qc.split("=") for qc in query.split("&"))
                username = query_components["username"]
                password = query_components["password"]
                if username:
                    print(username)
                if password:
                    print(password)
                cnx = mysql.connector.connect(user='testUser', password='Testing123!',
                                              host='127.0.0.1',
                                              database='it350')
                cursor = cnx.cursor()

                query = "select * from User WHERE username = '" + username + "' AND password = '" + password +"';"
                cursor.execute(query)
                obj = {}

                for (a, b, c, d, e, f, g, h) in cursor:
                    obj['id'] = a
                    obj['firstName'] = b
                    obj['lastName'] = c
                    obj['username'] = d
                    obj['password'] = e
                    obj['address'] = f
                    obj['email'] = g
                    obj['creditCard'] = h
                    self.wfile.write(bytes(obj.__str__(), "utf8"))
                if cursor.rowcount < 0:
                    self.wfile.write(bytes('not found', "utf8"))

                cursor.close()

                cnx.close()

            except (KeyError, ValueError):
                print('error')

        if path[0] == '/api/backup':
            try:
                print('bakcup')
                success = backup.run()
                self.wfile.write(bytes(success, "utf8"))
            except (KeyError, ValueError):
                print('error')
        if path[0] == '/api/showStatus':
            cnx = mysql.connector.connect(user='testUser', password='Testing123!',
                                          host='127.0.0.1',
                                          database='it350')

            cursor = cnx.cursor()

            query = "SHOW STATUS"
            cursor.execute(query)
            message = "<div id='status'>"
            for (Name, NUM) in cursor:
                message += ("<div>{}: {}</div>".format(
                    Name, NUM))

            message += "</div>"
            cursor.close()
            cnx.close()

            # Send message back to client
            # Write content as utf-8 data
            self.wfile.write(bytes(message, "utf8"))

        if path[0] == '/api/log':
            cnx = mysql.connector.connect(user='testUser', password='Testing123!',
                                          host='127.0.0.1',
                                          database='it350')
            cursor = cnx.cursor()

            query = "select * from mysql.general_log;"
            cursor.execute(query)
            message = "<div id='log'>"
            for (a, b, c, d, e, f) in cursor:
                message += ("<div>{} | {} | {} | {} | {} | {}</div>".format(
                    a, b, c, d, e, f))

            message += "</div>"
            cursor.close()

            cnx.close()

            # Send message back to client
            # Write content as utf-8 data
            self.wfile.write(bytes(message, "utf8"))

        if path[0] == '/api/mongoStatus':
            client = MongoClient('localhost', 27017)
            db = client['test']
            status = db.command('dbstats')
            self.wfile.write(bytes(status.__str__(), "utf8"))
        if path[0] == '/api/mongoUsage':
            client = MongoClient('localhost', 27017)
            db = client['inventory']
            status = db.command({'serverStatus': 1})
            self.wfile.write(bytes(status.__str__(), "utf8"))

        if path[0] == '/api/mongoBackup':
            os.system('mongodump --db inventory --out mongoBackup/dump')
            self.wfile.write(bytes("Backup Created in /mongoBackup/dump", "utf8"))

        if path[0] == '/api/esStatus':
            status = os.popen('curl localhost:9200/_cat/health').read()

            self.wfile.write(bytes(status.__str__(), "utf8"))
        if path[0] == '/api/esBackup':
            query = "curl -X PUT \"http://localhost:9200/_snapshot/my_backup\" -H 'Content-Type: application/json' -d'"
            query += "{\"type\": \"fs\", \"settings\": { \"location\": \"/var/es/repo\"}}'"
            status = os.popen(query)
            print(status)

        return


def run():
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()


run()
