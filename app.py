# -*- coding: utf-8 -*-
# Vezdekod22 - Marusya
import json

from flask import Flask, request
from flask_cors import CORS


DEV = True
CMDS = {
    '10': [
        'mosin вездекод',
        'мосин вездекод',
        'mosin вездеход',
        'мосин вездеход'
    ]
}
app = Flask(__name__)
cors = CORS(app, resources={
            '/': {"origins": '*',
                  "headers": 'Content-Type, Accept'}})


@app.route('/', methods=['GET', 'POST'])
def webhhook():
    req = request.get_json()
    if DEV:
        print(f'[REQUEST]: {req}')
    if req['request']['original_utterance'].lower() in CMDS['10']:
        return make_welcome(req)
    else:
        return make_echo(req)


def make_welcome(req: dict) -> str:
    resp = {
        'response': {
            'text': 'Привет вездекодерам!',
            'tts': 'Привет вездекодерам!',
            'end_session': False
        },
        'session': {
            'session_id': req['session']['session_id'],
            'user_id': req['session']['user_id'],
            'message_id': req['session']['message_id']
        },
        'version': req['version']
    }
    return json.dumps(resp)


def make_echo(req: dict) -> str:
    resp = {
        'response': {
            'text': req['request']['original_utterance'],
            'tts': req['request']['original_utterance'],
            'end_session': False
        },
        'session': {
            'session_id': req['session']['session_id'],
            'user_id': req['session']['user_id'],
            'message_id': req['session']['message_id']
        },
        'version': req['version']
    }
    return json.dumps(resp)
