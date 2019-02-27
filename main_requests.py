import lessons_db_manip
import Vk_bot
import schedule_parser


def make_answer(request):
    message = request.message.strip().lower()


if __name__ == '__main__':
    print(make_answer(lessons_db_manip.get_schedules(["10В"])))
