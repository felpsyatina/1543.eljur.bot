# -*- coding: utf-8 -*-

import json
import vk_api
import threading
from collections import deque
from vk_api.longpoll import VkLongPoll, VkEventType
import config


token = config.secret["vk"]["token"]
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
fail = "Простите, в нашем коде кто-то набагал. Мы скоро это исправим."
queue = deque()


def write_msg(u_id, mess):
    try:
        vk.method('messages.send', {'user_id': u_id, 'message': mess, 'v': "5.53"})
    except Exception:
        vk.method('messages.send', {'user_id': u_id, 'message': fail, 'v': "5.53"})


def write_key(u_id, keybor, mess="kek"):
    try:
        vk.method('messages.send', {
            'user_id': u_id,
            'message': mess,
            'keyboard': json.dumps(keybor, ensure_ascii=False),
            'v': "5.53"})
    except Exception:
        vk.method('messages.send', {'user_id': u_id, 'message': fail, 'v': "5.53"})


def _get_users_info_from_vk_ids(user_ids):
    string = ", ".join([str(i) for i in user_ids])
    return vk.method('users.get', {'user_ids' : string})


def make_key(a):
    try:
        buttons = []
        for raw in a:
            buttons.append([])
            for but in raw:
                if "color" in but.keys():
                    color = but["color"]
                else:
                    color = "default"
                button = {
                    "action": {
                      "type": "text",
                      "payload": "{\"button\": \"1\"}",
                      "label": but["text"]
                    },
                    "color": color
                }
                buttons[-1].append(button)
        return {
            "one_time": None,
            "buttons": buttons
        }
    except Exception:
        return None


def make_key_fast(s1, s2="", s3="", s4="", s5="", s6=""):
    try:
        a = []
        b = []
        for i in [s1, s2, s3, s4, s5, s6]:
            if i != "":
                a.append(i)
        for i in a:
            cur = i.split()
            curr = []
            for j in cur:
                curr.append({"text": j})
            b.append(curr)
        return make_key(b)
    except Exception:
        return {}


def go():
    global queue
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            queue.append({'user_id': event.user_id, 'message': event.text})


def run():
    threading.Thread(target=go).start()
    return


def get_next():
    global queue
    if len(queue) == 0:
        return None
    return queue.popleft()


def get_all():
    global queue
    if len(queue) == 0:
        return []
    cur = []
    while len(queue) != 0:
        cur.append(queue.popleft())
    return cur


if __name__ == '__main__':
    chels = [263235631]

    users = _get_users_info_from_vk_ids(chels)
    print(users)
    [print(user['first_name']) for user in users]