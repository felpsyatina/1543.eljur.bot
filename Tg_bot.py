import requests
import json
import time

TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
URL = 'https://api.telegram.org/bot' + TOKEN + '/'
raw_msgs = []
last_msg_id = -1
old_users = set()


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


def send_but_help(URL, user_id, text, msg_to_answer_id=None):
    url_send_msg = URL + 'sendmessage'
    reply_markup = json.dumps(
        {"keyboard": [['/help', '/help', '/help'], ['/help', '/help', '/help'], ['/help', '/help', '/help']],
         "one_time_keyboard": True})
    (requests.get(url_send_msg,
                  data={'chat_id': user_id, 'parse_mode': 'HTML', 'text': text, 'reply_markup': reply_markup,
                        'reply_to_message_id': msg_to_answer_id}))


def new_msgs(URL, last_msg_id, raw_msgs):
    url_new_msgs = URL + 'getupdates'
    msg_base = requests.get(url_new_msgs, data={"offset": last_msg_id}).json()
    if msg_base['ok'] == True and len(msg_base['result']) > 0:
        msg_base = msg_base['result']
        last_msg_id = (int(msg_base[-1]['update_id']) + 1)
        for i in range(len(msg_base)):
            tg_user_id = msg_base[i]['message']['from']['id']
            msg = msg_base[i]['message']['text']
            raw_msgs.append({'tg_user_id': tg_user_id, 'raw_msg': msg, 'msg_id': msg_base[i]['message']['message_id']})
    return last_msg_id, raw_msgs


def answer_msg(URL, user_id, msg, msg_id):
    if msg.startswith('/help'):
        send_msg(URL, user_id, "We can't help you :(", msg_id)
    else:
        send_but_help(URL, user_id, "Try to print /help", msg_id)


def answer_to_new_user(URL, user_id):
    send_but_help(URL, user_id, 'Hi, you are a new user. You can try to type /help')


def tg_bot_main(URL, last_msg_id, raw_msgs):
    print(bot_info(URL))
    while True:
        time.sleep(0.01)
        last_msg_id, raw_msgs = new_msgs(URL, last_msg_id, raw_msgs)
        if len(raw_msgs) > 0:
            msg_to_answer = raw_msgs[0]
            if msg_to_answer['tg_user_id'] in old_users:
                answer_msg(URL, msg_to_answer['tg_user_id'], msg_to_answer['raw_msg'], msg_to_answer['msg_id'])
            else:
                old_users.add(msg_to_answer['tg_user_id'])
                answer_to_new_user(URL, msg_to_answer['tg_user_id'])
            del raw_msgs[0]


if __name__ == '__main__':
    tg_bot_main(URL, last_msg_id, raw_msgs)

