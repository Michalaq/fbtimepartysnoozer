from flask import Flask, request, jsonify, url_for
app = Flask(__name__)

def model(j):
    return 'No siema'

@app.route("/")
def root():
    return 'Send chunks to {}'.format(url_for('answer'))

@app.route("/answer", methods=['POST'])
def answer():
    if not request.is_json:
        return "JSON required!"

    j = request.get_json()
    return jsonify({'ans': model(j), 'data': j})
