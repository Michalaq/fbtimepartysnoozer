# -*- coding: utf-8 -*-

import random
from flask import Flask, request, jsonify, url_for
app = Flask(__name__)

def model(j):
    # return u'No siema, twoja przedostatnia wiadomość to {}'.format(j['messages'][1]['content'])
    return random.sample(["Okay", "I understand", "Sure, why not?", "Thanks for coming", "Sounds good"], 1)

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
