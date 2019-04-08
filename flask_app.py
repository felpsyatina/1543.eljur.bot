from __future__ import unicode_literals
import json
import logger
import user_req


from flask import Flask, request
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

