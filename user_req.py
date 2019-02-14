import logger
import lessons_db_manip as ldm
import schedule_parser as sp
import answers_dict as ad
import users_db_parser as ud
from random import randint


def update_schedule():
    schedule = sp.get_current_schedule()
    ldm.add_schedules(schedule)
    return


def get_schedule(scr, user_id, text):
    schedule = ldm.get_schedule(get_class_name_from_text(text.upper()))
    answer_string = ""
    for day_name, day_schedule in schedule.items():
        answer_string += str(day_name.title()) + ':\n'
        for lesson_num in day_schedule.keys():
            answer_string += str(lesson_num) + '. ' + str(day_schedule[lesson_num][1]) + str(day_schedule[lesson_num][8]) + '\n'
    return answer_string


def get_class_name_from_text(text):
    class_name = text.split()[1]
    return class_name


def get_day_and_lesson_and_class_name_from_text(text):    # отмена lesson в day у class_name
    day = text.split()[3]
    lesson = text.split()[1]
    class_name = text.split()[5]
    return day, lesson, class_name


def generate_return(text):
    return {"text": text, "buttons": None}


def send_acc_information(src, user_id, text):
    logger.log("user_req", "request for acc data")
    ans_mes = ud.get_user_by_id(src, user_id)
    answer_message = f"Логин:{ans_mes[1]}\nИмя:{ans_mes[3]}\nФамилия:{ans_mes[4]}\nПараллель:{ans_mes[1]}"
    return answer_message


def cancel_lesson(src, user_id, text):
    logger.log("user_req", "cancelling a lesson")
    day, lesson, class_name = get_day_and_lesson_and_class_name_from_text(text)
    ldm.get_cancel(class_name, day, lesson)
    return "Урок отменен"




def parse_message_from_user(scr, user_id, text):
    logger.log("user_req", "process request")
    text = text.strip().lower()
    try:
        for key, value in ad.quest.items():
            if key in text:
                needed_function = key_words_to_function[value]
                answer_from_function = needed_function(scr, user_id, text)
                return generate_return(answer_from_function)
                # generate_return(ldm.get_schedule())
        logger.log("user_req", f"Запрос не найден. Запрос: {text}")
        return {"text": "Запроса не найдено :( ", "buttons": None}

    except Exception as err:
        logger.log("user_req", f"Processing error: {err}\n Запрос: {text}")
        return {"text": "Видно, не судьба :( ", "buttons": None}


key_words_to_function = {"schedule": get_schedule,
                         # "registration": register_new_user,
                         "account": send_acc_information,
                         "cancel": cancel_lesson,
                         # "replacement": replace_lesson,
                         # "comment": comment_lesson,
                         # "support": support_message,
                         # "commands": send_commands
                         }
# update_schedule()
# parse_message_from_user("tg", "1", "УМРИ")

# ya LOH_KABAKOV
