# -*- coding: utf-8 -*-
# Vezdekod22 - Marusya
import os
import sys
import json
import logging
from enum import IntEnum
from tabnanny import check

from flask import Flask, request
from flask_cors import CORS

from vk_api import VKApi
from database import Database


DEV = False
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
            '<speaker audio=marusia-sounds/game-boot-1>Сейчас мы узнаем какая категория Вездекода вам подойдёт!\n\nВы любите Gamedev?\nОтветьте Да или Нет.',
            'Ладно. Как думаете, Java лучший язык программирования?\nОтветьте Да или Нет.',
            'Ну хорошо. А вам нравится разрабатывать мобильные приложения?\nОтветьте Да или Нет.',
            'Окей. Как думаете, PHP лучший язык программирования?\nОтветьте Да или Нет.',
            'Понятно. А вам нравится разрабатывать Back End?\nОтветьте Да или Нет.',
            'Ладно. А вам нравится разрабатывать скилы для Маруси?\nОтветьте Да или Нет.',
            'Понимаю. Как думаете, чат-боты спасут мир?\nОтветьте Да или Нет.',
            'Ясно. А вы любите VK Mini Apps?\nОтветьте Да или Нет.'
        ]
    },
    '50': [
        'регистрация на вездекод',
        'регистрация на вездеход'
    ]
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
    LOVELY_MEME = 8


app = Flask(__name__)
cors = CORS(app, resources={
            '/': {"origins": '*',
                  "headers": 'Content-Type, Accept'}})
logging.basicConfig(
    format='[%(asctime)s] (%(levelname)s) %(name)s.%(funcName)s (%(lineno)d) >> %(message)s',
    level=logging.DEBUG if DEV else logging.INFO)
log = logging.getLogger('server')
db = Database()
if 'SKILL_TOKEN' in os.environ:
    vka = VKApi(os.environ.get('SKILL_TOKEN', ''))
    resp = vka.marusia_getPictures()
    if resp:
        log.info('Logged in VK Api as Skill.')
    else:
        log.fatal(f'Can\'t login to VK Api as Skill!\nResponse: {resp}')
        sys.exit(1)
else:
    log.fatal('Can\'t work without skill service key "env: SKILL_TOKEN"!')
    sys.exit(1)


def check_db():
    log.debug('Creating tables in DB...')
    db._create_tables()
    log.debug('Checking photos in DB...')
    for cat in VK_CATS:
        if not db.get_category_photo(cat.value):
            with open(f'photos/{cat.value}.jpg', 'rb') as f:
                pic_id = vka.uploadPicture(f)
            if pic_id:
                db.add_photo(pic_id, cat.value)
            else:
                log.fatal('Can\'t upload picture to Skill media\'s!')
                sys.exit(1)
    log.debug('Checking complete!')


check_db()


@app.route('/_webhooks/marusya/vezdekod22/', methods=['GET', 'POST'])
def webhhook():
    req = request.get_json()
    log.debug(f'New request: {req}')
    utter = req['request']['original_utterance'].lower()
    if utter in CMDS['10']:
        return make_welcome(req)
    elif utter == 'вопросы' or req['state']['session']:
        return make_questions(req)
    elif utter in CMDS['50']:
        return make_register(req)
    elif utter == 'открыть приложение регистрации':
        return make_app(req)
    elif req['session']['new']:
        return make_welcome(req)
    else:
        return make_echo(req)


def make_app(req: dict) -> str:
    resp = {
        'response': {
            'text': 'Открываю приложение регистрации Вездекода.',
            'tts': 'Открываю приложение регистрации Вездекода.',
            'end_session': True,
            'card': {
                'type': 'MiniApp',
                'url': 'https://vk.com/app7543093'
            }
        },
        'session': {
            'session_id': req['session']['session_id'],
            'user_id': req['session']['user_id'],
            'message_id': req['session']['message_id']
        },
        'version': req['version']
    }
    return json.dumps(resp)


def make_register(req: dict) -> str:
    m = 'Ты можешь зарегистрироваться на вездекоде в приложении!\n\nЗаодно, лови мой любимый мем из Конкурса Мемов!'
    resp = {
        'response': {
            'text': m,
            'tts': m,
            'end_session': False,
            'card': {
                'type': 'BigImage',
                'image_id': db.get_category_photo(VK_CATS.LOVELY_MEME.value)
            },
            'buttons': [
                {
                    'title': 'Открыть приложение регистрации',
                    'action': {
                        'type': 'open_mini_app',
                        'app_id': 7543093
                    }
                }
            ]
        },
        'session': {
            'session_id': req['session']['session_id'],
            'user_id': req['session']['user_id'],
            'message_id': req['session']['message_id']
        },
        'version': req['version']
    }
    return json.dumps(resp)


def make_welcome(req: dict) -> str:
    resp = {
        'response': {
            'text': 'Привет вездекодерам!\n\nХочешь узнать какую категорию вездекода тебе лучше выбрать? Спроси у меня "Вопросы"!\nА если хочешь зарегистрироваться на Вездекод, скажи "Регистрация на Вездекод".',
            'tts': '<speaker audio=marusia-sounds/music-tambourine-120bpm-1>Привет вездекодерам!\n\nХочешь узнать какую категорию вездекода тебе лучше выбрать? Спроси у меня "Вопросы"!\nА если хочешь зарегистрироваться на Вездекод, скажи "Регистрация на Вездекод".',
            'end_session': False,
            'buttons': [
                {'title': 'Вопросы'},
                {'title': 'Регистрация на Вездекод'}
            ]
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
        'yes': 'Спасибо за ответ!\nДумаю вам больше подойдёт категория:<speaker audio=marusia-sounds/music-drums-3> {}.\nУдачного вездекодинга!',
        '404': 'Спасибо за ответы!\nК сожалению, вам не подходит не одна из категорий вездекода.\nНе переживайте, я уверена на следующий вездекод найдётся категория которая будет вам по душе!'
    }
    end_state = False
    if req['state']['session']:
        cur_state = VK_CATS(req['state']['session']['cat'])
        utter = req['request']['original_utterance'].lower()
        log.debug(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} says {utter}')
        log.debug(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} on state {cur_state.name}')
        if utter == 'да':
            tts = TEXTS['yes'].format(_get_cat_name(cur_state))
            text = tts.replace('<speaker audio=marusia-sounds/music-drums-3>', '')
            end_state = True
        else:
            if cur_state.value == 7:
                text = TEXTS['404']
                tts = f'<speaker audio=marusia-sounds/game-loss-3> {text}'
                end_state = True
            else:
                cur_state = VK_CATS(cur_state + 1)
                log.debug(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} on a new state {cur_state.name}')
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
                'end_session': False,
                'buttons': [
                    {'title': 'Да'},
                    {'title': 'Нет'}
                ]
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
        log.debug(f'[SESSION #{req["session"]["session_id"]}] User #{req["session"]["user_id"]} out from states.')
        resp = {
            'response': {
                'text': text,
                'tts': tts,
                'end_session': False,
                'card': {
                    'type': 'BigImage',
                    'image_id': db.get_category_photo(cur_state.value)
                }
            },
            'session': {
                'session_id': req['session']['session_id'],
                'user_id': req['session']['user_id'],
                'message_id': req['session']['message_id']
            },
            'version': req['version']
        }
    return json.dumps(resp)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

