from __future__ import unicode_literals

import json

from flask import Flask, request
from flask import render_template

import functions
import logger
import user_req
from lessons_db_manip import LessonDbReq

app = Flask(__name__)

sessionStorage = {}


@app.route("/", methods=['POST'])
def main():
    logger.log('eljur_flask_app.py', 'new request')

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logger.log('eljur_flask_app.py', f"response '{response}'")

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def handle_dialog(req, res):
    if req['session']['new']:
        # Это новый пользователь.
        res['response']['text'] = 'Привет! Что ты хочешь узнать?'
        return

    user_dict = {
        "first_name": 'Lol',
        "last_name": 'Kekevich',
        "sex": '',
        "src": "alice",
        "id": req['session']['user_id'],
        "text": req['request']['command'],
    }
    try:
        res['response']['text'] = user_req.parse_message_from_user(user_dict)['text']
        return
    except Exception as err:
        logger.log('eljur_flask_app.py', 'error:', str(err))


def short_name(string):
    arr = string.split()
    for i in range(1, len(arr)):
        arr[i] = arr[i][0] + '.'
    return " ".join(arr)


@app.route('/desk')
def display():
    req = LessonDbReq()
    lesson_number = request.args.to_dict()
    lessons = req.get_beautified_lessons_for_desk(**lesson_number)
    for lesson in lessons:
        if lesson['teacher'] is not None:
            lesson['teacher_short'] = short_name(lesson['teacher'])
    new_lessons = {}
    for class_name in functions.classes:
        new_lessons[class_name] = []
    for lesson in lessons:
        new_lessons[lesson['class_name']] += [lesson]
    new_lessons = sorted(new_lessons.items(), key=lambda x: int(x[0][:-1]))

    return render_template('desk.html', lessons=new_lessons)


if __name__ == '__main__':
    app.run()
