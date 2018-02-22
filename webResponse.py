from flask import Flask, request
import requests
import psycopg2
import os
from urllib import parse

# Connecting to postgres DATABASE
parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
cur = conn.cursor()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def startup():
    msg = """"""
    cur.execute('SELECT * FROM ideas;')
    rows = cur.fetchall()
    for row in rows:
        msg += '{}<br>'.format(row)
    return msg, 200

if __name__ == '__main__':
    app.run(debug=True)
