# -*- coding: utf-8 -*-

import random
from flask import Flask, request, jsonify, url_for
import pickle
app = Flask(__name__)

def sanitize(slowo):
    tab = {
        'ą': 'a',
        'ł': 'l',
        'ć': 'c',
        'ź': 'z',
        'ż': 'z',
        'ę': 'e',
        'ó': 'o',
        'ś': 's',
        'ń': 'n',
        '?': None,
        '!': None,
    }
    tab = { ord(k): v for k, v in tab.items() }
    return slowo.translate(tab).strip()

with open('baza.pkl', 'rb') as f:
    baza = pickle.loads(f.read())

def model(j):
    # return u'No siema, twoja przedostatnia wiadomość to {}'.format(j['messages'][1]['content'])
    return random.sample(baza[sanitize(j['messages'][0]['content'])], 1)
    # return random.sample(["Okay", "I understand", "Sure, why not?", "Thanks for coming", "Sounds good"], 1)

# chat api -> model format
def process(j):
    history = j['history']
    myId = j['myId']

    def processOne(entry):
        return {
            'content': entry['body'],
            'isMe': entry['senderID'] == myId,
            'timestamp': entry['timestamp']
        }

    return {
        'messages': [processOne(e) for e in sorted(history, key=lambda k: k['timestamp'], reverse=True)]
    }

@app.route("/")
def root():
    return 'Send chunks to {}'.format(url_for('answer'))

@app.route("/answer", methods=['POST'])
def answer():
    if not request.is_json:
        return "JSON required!"

    j = request.get_json()
    processed = process(j)
    ans = model(processed)

    return jsonify({'processed': processed, 'ans': ans})
