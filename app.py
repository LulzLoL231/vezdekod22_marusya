# -*- coding: utf-8 -*-
# Vezdekod22 - Marusya
import json
from enum import IntEnum

from flask import Flask, request
from flask_cors import CORS


DEV = True
CMDS = {
    '10': [
        'mosin вездекод',
        'мосин вездекод',
        'mosin вездеход',
        'мосин вездеход'
    ],
    '20': {
        'cats': [
            'Gamedev', 'Java', 'Mobile', 'PHP', 'Back End', 'Маруся',
            'Чат-боты', 'VK Mini Apps'
        ],
        'questions': [
            'Сейчас мы узнаем какая категория Вездекода вам подойдёт!\n\nВы любите Gamedev?\nОтветьте Да или Нет.',
            'Ладно, Java лучший язык программирования?\nОтветьте Да или Нет.',
            'Ну хорошо, а вам нравится разрабатывать мобильные приложения?\nОтветьте Да или Нет.',
            'Окей, как думаете, PHP лучший язык программирования?\nОтветьте Да или Нет.',
            'Понятно, а вам нравится разрабатывать Back End?\nОтветьте Да или Нет.',
            'Ладно, а вам нравится разрабатывать скилы для Маруси?\nОтветьте Да или Нет.',
            'Понимаю, как думаете, чат-боты спасут мир?\nОтветьте Да или Нет.',
            'Ясно, а вы любите VK Mini Apps?\nОтветьте Да или Нет.'
        ]
    }
}


class VK_CATS(IntEnum):
    GAMEDEV = 0
    JAVA = 1
    MOBILE = 2
    PHP = 3
    BACKEND = 4
    MARUSIA = 5
    BOTS = 6
    APPS = 7


app = Flask(__name__)
cors = CORS(app, resources={
            '/': {"origins": '*',
                  "headers": 'Content-Type, Accept'}})


@app.route('/', methods=['GET', 'POST'])
def webhhook():
    req = request.get_json()
    if DEV:
        print(f'[REQUEST]: {req}')
    utter = req['request']['original_utterance']
    if utter.lower() in CMDS['10']:
        return make_welcome(req)
    elif utter.lower() == 'вопросы' or req['state']['session']:
        return make_questions(req)
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


def _get_cat_name(cat: VK_CATS) -> str:
    return CMDS['20']['cats'][cat.value]  # type: ignore


def make_questions(req: dict) -> str:
    TEXTS = {
        'yes': 'Спасибо за ответ!\nДумаю вам больше подойдёт категория: {}.\nУдачного вездекодинга!',
        '404': 'Спасибо за ответы!\nК сожалению, вам не подходит не одна из категорий вездекода.\nНе переживайте, я уверена на следующий вездекод найдётся категория которая будет вам по душе!'
    }
    end_state = False
    if req['state']['session']:
        cur_state = VK_CATS(req['state']['session']['cat'])
        utter = req['request']['original_utterance'].lower()
        if DEV:
            print(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} says {utter}')
            print(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} on state {cur_state.name}')
        if utter == 'да':
            text = TEXTS['yes'].format(_get_cat_name(cur_state))
            tts = text
            end_state = True
        else:
            if cur_state.value == 7:
                text = TEXTS['404']
                tts = text
                end_state = True
            else:
                cur_state = VK_CATS(cur_state + 1)
                if DEV:
                    print(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} on a new state {cur_state.name}')
                text = CMDS['20']['questions'][cur_state.value]  # type: ignore
                tts = text
    else:
        cur_state = VK_CATS.GAMEDEV
        text = CMDS['20']['questions'][cur_state.value]  # type: ignore
        tts = text
    if not end_state:
        session_state = {
            'cat': cur_state.value
        }
        resp = {
            'response': {
                'text': text,
                'tts': tts,
                'end_session': False
            },
            'session': {
                'session_id': req['session']['session_id'],
                'user_id': req['session']['user_id'],
                'message_id': req['session']['message_id']
            },
            'session_state': session_state,
            'version': req['version']
        }
    else:
        if DEV:
            print(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} out from states.')
        resp = {
            'response': {
                'text': text,
                'tts': tts,
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
