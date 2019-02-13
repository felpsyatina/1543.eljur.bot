import requests
import json
import time
import user_req
import config
import logger

TOKEN = config.secret["tg"]["token"]
URL = 'https://api.telegram.org/bot' + TOKEN + '/'
raw_msgs = []
last_msg_id = -1


def bot_info(URL):
    url_get_me = URL + 'getme'
    bot_info = requests.get(url_get_me).json()
    return bot_info


def bot_upd(URL):
    url_upd = URL + 'getupdates'
    bot_upd = requests.get(url_upd).json()
    return bot_upd


def send_msg(URL, user_id, text, msg_to_answer_id=None):
    url_send_msg = URL + 'sendmessage'
    requests.get(url_send_msg, data={'chat_id': user_id, 'text': text, 'reply_to_message_id': msg_to_answer_id})


def send_but_help(URL, user_id, text, keyb_but, msg_to_answer_id=None):
    url_send_msg = URL + 'sendmessage'
    reply_markup = json.dumps(
        {"keyboard": keyb_but,
         "one_time_keyboard": True})
    (requests.get(url_send_msg,
                  data={'chat_id': user_id, 'parse_mode': 'HTML', 'text': text, 'reply_markup': reply_markup,
                        'reply_to_message_id': msg_to_answer_id}))


def new_msgs(URL, last_msg_id, raw_msgs):
    url_new_msgs = URL + 'getupdates'
    msg_base = requests.get(url_new_msgs, data={"offset": last_msg_id}).json()
    if msg_base['ok'] == True and len(msg_base['result']) > 0:
        logger.log("tg", "getting new messages")
        msg_base = msg_base['result']
        last_msg_id = (int(msg_base[-1]['update_id']) + 1)
        for i in range(len(msg_base)):
            tg_user_id = msg_base[i]['message']['from']['id']
            msg = msg_base[i]['message']['text']
            raw_msgs.append({'tg_user_id': tg_user_id, 'raw_msg': msg, 'msg_id': msg_base[i]['message']['message_id']})
    return last_msg_id, raw_msgs


def answer_msg(URL, user_id, msg, msg_id):
    logger.log("tg", "sending message to "+str(user_id))
    result = user_req.parse_message_from_user("tg", user_id, msg)
    msg_to_send = result['text']
    send_msg(URL, user_id, msg_to_send, msg_id)

def tg_bot_main(URL, last_msg_id, raw_msgs):
    print(bot_info(URL))
    logger.log("tg", "starting tg_bot")
    while True:
        time.sleep(1)
        last_msg_id, raw_msgs = new_msgs(URL, last_msg_id, raw_msgs)
        if len(raw_msgs) > 0:
            for i in range(len(raw_msgs)):
                msg_to_answer = raw_msgs[i]
                answer_msg(URL, msg_to_answer['tg_user_id'], msg_to_answer['raw_msg'], msg_to_answer['msg_id'])
            raw_msgs=[]


if __name__ == '__main__':
    tg_bot_main(URL, last_msg_id, raw_msgs)
