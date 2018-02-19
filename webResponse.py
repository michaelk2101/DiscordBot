from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def startup():
    msg = """"""
    with open('ideas.txt', 'r') as f:
        data = list(f.readlines())
    for item in data:
        msg += '{}<br>'.format(item)
    return msg, 200

if __name__ == '__main__':
    app.run(debug=True)
