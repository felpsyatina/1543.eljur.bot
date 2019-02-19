import users_db_parser
import Vk_bot
import Tg_bot
import logger


def send_alerts(a, mess):
    vk = []
    tg = []
    for id in a:
        info = users_db_parser.get_user_by_global_id(id)
        vk_id = info[8]
        tg_id = info[10]
        if vk_id:
            vk.append(vk_id)
        if tg_id:
            tg.append(tg_id)
    logger.log("alerts", "alerts formed: vk_users: " + str(len(vk)) + " tg_users: " + str(len(tg)))
    logger.log("alerts", "alerts formed: vk_ids: " + str(vk) + " tg_ids: " + str(vk))
    Vk_bot.alerts(vk, mess)
    Tg_bot.alerts(tg, mess)
