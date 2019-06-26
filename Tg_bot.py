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
DELAYS = {
    # все задержки задаются в секндах, могут быть дробными
    "BETWEEN_MESSAGES_IN_MAILING": 1,  # задуржки между сообщениями в alerts рассылке
    "BETWEEN_POLLING_REQUESTS": 2,  # задержки между запросами обновлений к телеграму
    "BETWEEN_TEST_CONNECTION_ATTEMPTS": 5,  # задержка между тестовыми запросоми к серверу во время старта модуля
}


def check_telegram_availability():
    """
    Функция отправляет тестовый запрос getme серверу и проверяет ответ. Если телеграм ответил, и ответ был
    хороший функция возвращает true, иначе false.
    """
    try:
        telegram_answer = requests.get(url_get_me).json()
        if telegram_answer["ok"]:
            return True
        else:
            logger.log("tg",
                       f"check_telegram_availability: connection was established, but answer is bad: {telegram_answer}")
            return False
    except Exception as exc:
        logger.log("tg", f"check_telegram_availability: failed to establish connection with telegram server err: {exc}")
        return False


def alerts(user_ids_for_alert_mailing, message):
    """
    Функция рассылки однинакового сообщения всем пользователем переданного списка
    :param user_ids_for_alert_mailing: list of used_ids, кому будет отправлено сообщение
    :param message:
    """
    for user_id in user_ids_for_alert_mailing:
        time.sleep(DELAYS["BETWEEN_MESSAGES_IN_MAILING"])
        send_message(user_id, message)
        logger.log("tg", f"sending alert to {user_id}")


def bot_upd():
    bot_upd = requests.get(url_upd).json()
    return bot_upd


def is_valid_default_keyboard_markup(default_keyboard_markup):
    """
    Проверяет валидность дефолтной клавиатуры:
    list/tuple( list/tuple( list/tuple() ) ) -> True
    всё остальное                            -> False
    """
    return isinstance(default_keyboard_markup, (list, tuple)) \
           and all(isinstance(row, (list, tuple)) for row in default_keyboard_markup) \
           and all(all(isinstance(button, (list, tuple)) for button in row) for row in default_keyboard_markup)


def converter_to_telegram_keyboard_markup(default_keyboard_markup):
    """
    Функция преобразовывает дефолтную клавиатуру, пzмает только текст клавиши, все остальные параметры
    он исполнить не может, поэтому требует вместо массива только строку с текстом клавиши.

    Преобразование кнопки:
    ['button_text', 3, ...] -> 'button_text'

    Для всей клавиатуры это выглядит так:
    [ [['7', 1, ..], ['8', 0, ..], ['9', 3, ..]],     [ ['7', '8', '9'],
      [['4', 1, ..], ['5', 3, ..], ['6', 1, ..]],  ->   ['4', '5', '6'],
      [['1', 2, ..], ['2', 1, ..], ['3', 0, ..]],       ['1', '2', '3'],
                  [['0', 3, ..]] ];                          ['0'] ];

    :param default_keyboard_markup: дефолтная клавиатура
    :return telegram_keyboard_markup: правильная telegram-клавиатура или None в случае, если клавиатура не валидна
    """
    # проверка валидности
    if not is_valid_default_keyboard_markup(default_keyboard_markup):
        logger.log("new_tg",
                   f"fix_board: unexpected keyboard markup type got keyboard {default_keyboard_markup} "
                   f"expected like list/tuple( list/tuple( list/tuple() ) )")
        return None

    # преобразование клавиатуры
    telegram_keyboard_markup = list([str(button[0]) for button in row] for row in default_keyboard_markup)

    return telegram_keyboard_markup


def send_message(user_id, text, default_keyboard_markup=None, msg_to_answer_id=None):
    """
    Функция отправки сообщения пользователю
    :param user_id: id диалога бота с получателем
    :param text:
    :param default_keyboard_markup:
    :param msg_to_answer_id: id сообщения, пересылкой которого будет новое
    """
    telegram_keyboard_markup = converter_to_telegram_keyboard_markup(
        default_keyboard_markup) if default_keyboard_markup is not None else None
    reply_markup = json.dumps(
        {"keyboard": telegram_keyboard_markup,
         "one_time_keyboard": True})
    logger.log("tg", f"send msg - {str(text)} and but - {str(telegram_keyboard_markup)} to {str(user_id)}")
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
            if 'text' in msg_base[i]['message']:
                msg = msg_base[i]['message']['text']
            else:
                msg = ''
            msg_id = msg_base[i]['message']['message_id']
            if 'last_name' in msg_base[i]['message']['from']:
                user_name = {'first_name': msg_base[i]['message']['from']['first_name'],
                             'last_name': msg_base[i]['message']['from']['last_name']}
            else:
                user_name = {'first_name': msg_base[i]['message']['from']['first_name'],
                             'last_name': ''}
            logger.log("tg", f"get message - {msg} from {str(tg_user_id)}")
            raw_msgs.append({'tg_user_id': tg_user_id, 'raw_msg': msg, 'msg_id': msg_id, 'user_name': user_name,
                             'is_super_admin': super_admin})
    else:
        is_new_msgs = False
    return is_new_msgs, last_msg_id, raw_msgs


def answer_msg(user_id, msg, msg_id, user_name):
    try:
        result = user_req.parse_message_from_user(
            {'src': "tg", 'id': user_id, 'text': msg, 'sex': '0', 'first_name': user_name['first_name'],
             'last_name': user_name['last_name']})
        logger.log("tg", f"got message from user_req: {str(result['text'])} {str(result.get('buttons'))}")

    except Exception as err:
        result = {"text": "error", "buttons": [[]]}
        logger.log("tg", f"couldn't get message from user_req: {str(err)}")
    msg_to_send = result['text']
    but_to_send = result.get('buttons', [[]])
    if type(result['text']) is str:
        send_message(user_id, msg_to_send, but_to_send, msg_id)
    else:
        for i in range(len(msg_to_send)):
            msg_to_send_now = msg_to_send[i]
            send_message(user_id, msg_to_send_now, but_to_send, msg_id)


def tg_bot_main(last_msg_id, raw_msgs):
    logger.log("tg", "tg_bot is starting... Please, wait for OK")
    while check_telegram_availability():
        logger.log("tg", f"tg_bot_main: connection to telegram failed, next attempt will be in "
                   + str(DELAYS['BETWEEN_TEST_CONNECTION_ATTEMPTS']) + " seconds")
        time.sleep(DELAYS['BETWEEN_TEST_CONNECTION_ATTEMPTS'])

    logger.log("tg", "tg_bot_main: OK. bot has been started to work")
    while True:
        time.sleep(DELAYS["BETWEEN_POLLING_REQUESTS"])
        is_new_msgs, last_msg_id, raw_msgs = new_msgs(last_msg_id, raw_msgs)
        if is_new_msgs:
            for i in range(len(raw_msgs)):
                msg_to_answer = raw_msgs[i]
                if msg_to_answer['is_super_admin'] == '0':
                    answer_msg(msg_to_answer['tg_user_id'], msg_to_answer['raw_msg'], msg_to_answer['msg_id'],
                               msg_to_answer['user_name'])
                else:
                    send_message(msg_to_answer['tg_user_id'], 'you are super admin', msg_to_answer['msg_id'])
                    answer_msg(msg_to_answer['tg_user_id'], msg_to_answer['raw_msg'], msg_to_answer['msg_id'],
                               msg_to_answer['user_name'])
            raw_msgs = []


if __name__ == '__main__':
    tg_bot_main(last_msg_id, raw_msgs)
