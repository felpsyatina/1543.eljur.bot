import requests
import logger
from bs4 import BeautifulSoup

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А', '9Б',
           '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']
DAYS = 6
CNT_LESSONS = 7


def get_current_schedule():
    schedule = {}

    for i in classes:
        print(i)
        page = requests.get('https://1543.eljur.ru/class.' + i + '/startdate.2019-01-21/journal-schedule-action')
        soup = BeautifulSoup(page.text, 'html.parser')

        schedule_for_class = {}

        for j in range(DAYS):
            schedule_html = soup.find(class_='schedule__day__content')
            day_list = schedule_html.find_all('p')[1]
            day = day_list.contents[0]
            lessons_this_day = schedule_html.find_all(class_='schedule__day__content__lesson__data')
            lessons = {}
            for k in range(len(lessons_this_day)):
                lessons[k + 1] = lessons_this_day[k].find_all('span')[0].contents[0].strip()
            schedule_for_class[day] = lessons
            schedule_html.decompose()
        schedule[i] = schedule_for_class
    return schedule


if __name__ == '__main__':
    schedule = get_current_schedule()
    print(schedule)
    # Пример:
    while 1:
        cl = input()
        day = input()
        for k in range(CNT_LESSONS):
            print(schedule[cl][day][k])
