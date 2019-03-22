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
super_admins = {183534296}
url_get_me = URL + 'getme'
url_upd = URL + 'getupdates'
url_send_msg = URL + 'sendmessage'
url_new_msgs = URL + 'getupdates'


def bot_info():
    print(URL)
    bot_info = requests.get(url_get_me).json()
    return bot_info


def alerts(alerts_ids, msg):
    for i in range(len(alerts_ids)):
        time.sleep(1)
        user_id = alerts_ids[i]
        send_msg(user_id, msg)
        logger.log("tg", "sending alert to" + user_id)


def bot_upd():
    bot_upd = requests.get(url_upd).json()
    return bot_upd


def send_msg(user_id, text, msg_to_answer_id=None):
    requests.get(url_send_msg, data={'chat_id': user_id, 'text': text, 'reply_to_message_id': msg_to_answer_id})


def fix_board(board):
    if type(board) == int:
        return board

    ans = []
    logger.log("tg", f"BOARDS!!!!!! {board}")
    for x in board:
        tmp = []
        for y in x:
            tmp.append(str(y))
        ans.append(tmp)

    logger.log("tg", f"ANSS!!!!!! {ans}")
    return ans


def send_msg_and_but(user_id, text, keyb_but, msg_to_answer_id=None):
    reply_markup = json.dumps(
        {"keyboard": fix_board(keyb_but),
         "one_time_keyboard": True})
    logger.log("tg", str(reply_markup))
    (requests.get(url_send_msg,
                  data={'chat_id': user_id, 'text': text, 'reply_markup': reply_markup,
                        'reply_to_message_id': msg_to_answer_id}))


def new_msgs(last_msg_id, raw_msgs):
    msg_base = requests.get(url_new_msgs, data={"offset": last_msg_id}).json()
    if msg_base['ok'] == True and msg_base['result'] != []:
        is_new_msgs = True
        logger.log("tg", "getting new messages")
        msg_base = msg_base['result']
        last_msg_id = (int(msg_base[-1]['update_id']) + 1)
        for i in range(len(msg_base)):
            tg_user_id = msg_base[i]['message']['from']['id']
            if tg_user_id in super_admins:
                super_admin = '1'
            else:
                super_admin = '0'
            msg = msg_base[i]['message']['text']
            msg_id = msg_base[i]['message']['message_id']
            if 'last_name' in msg_base[i]['message']['from']:
                user_name = {'first_name': msg_base[i]['message']['from']['first_name'],
                             'last_name': msg_base[i]['message']['from']['last_name']}
            else:
                user_name = {'first_name': msg_base[i]['message']['from']['first_name'],
                             'last_name': ''}
            logger.log("tg", "get message - " + msg + " from" + str(tg_user_id))
            raw_msgs.append({'tg_user_id': tg_user_id, 'raw_msg': msg, 'msg_id': msg_id, 'user_name': user_name,
                             'is_super_admin': super_admin})
    else:
        is_new_msgs = False
    return is_new_msgs, last_msg_id, raw_msgs


def answer_msg(user_id, msg, msg_id, user_name):
    logger.log("tg", "sending message to " + str(user_id))
    try:
        result = user_req.parse_message_from_user("tg", user_id, msg, user_name)
        logger.log("tg", "message: " + str(result['text']) + str(result['buttons']))

    except Exception as err:
        result = {"text": "error", "buttons": None}
        logger.log("tg", f"error: {str(err)}")

    msg_to_send = result['text']
    but_to_send = result['buttons']
    send_msg_and_but(user_id, msg_to_send, but_to_send, msg_id)


def tg_bot_main(last_msg_id, raw_msgs):
    logger.log("tg", "starting tg_bot")
    bot_info()
    while True:
        time.sleep(2)
        is_new_msgs, last_msg_id, raw_msgs = new_msgs(last_msg_id, raw_msgs)
        if is_new_msgs:
            for i in range(len(raw_msgs)):
                msg_to_answer = raw_msgs[i]
                if msg_to_answer['is_super_admin'] == '0':
                    answer_msg(msg_to_answer['tg_user_id'], msg_to_answer['raw_msg'], msg_to_answer['msg_id'],
                               msg_to_answer['user_name'])
                else:
                    send_msg_and_but(msg_to_answer['tg_user_id'], 'you are super admin', msg_to_answer['msg_id'])
                    answer_msg(msg_to_answer['tg_user_id'], msg_to_answer['raw_msg'], msg_to_answer['msg_id'],
                               msg_to_answer['user_name'])
            raw_msgs = []


def run_tg_bot():
    try:
        tg_bot_main(last_msg_id, raw_msgs)
    except Exception as err:
        logger.log("tg", "tg brokes down. Processing error: " + str(err))
        time.sleep(5)
        run_tg_bot()


if __name__ == '__main__':
    run_tg_bot()


