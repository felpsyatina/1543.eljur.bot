import requests
from bs4 import BeautifulSoup

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А', '9Б',
           '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']
days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
error_msg = "Извините, произошла ошибка :("
schedule = []
schedule2 = {}


for i in classes:
    print(i)
    page = requests.get('https://1543.eljur.ru/class.' + i + '/startdate.2019-01-14/journal-schedule-action')
    soup = BeautifulSoup(page.text, 'html.parser')

    schedule_for_class = []
    schedule_for_class2 = {}

    for j in range(6):
        schedule_html = soup.find(class_='schedule__day__content')
        day_list = schedule_html.find_all('p')[1]
        day = day_list.contents[0]
        lessons_this_day = schedule_html.find_all(class_='schedule__day__content__lesson__data')
        lessons = []
        for k in range(len(lessons_this_day)):
            lessons.append(lessons_this_day[k].find_all('span')[0].contents[0])
        schedule_for_class.append({day: lessons})
        schedule_for_class2[day] = lessons
        schedule_html.decompose()
    schedule.append({i: schedule_for_class})
    schedule2[i] = schedule_for_class2

print(schedule)
print(schedule2)


# while 1:
#     inp_class = input("Введите класс: ")
#     inp_class_schedule = schedule2.get(inp_class, -1)
#
#     if inp_class_schedule == -1:
#         print(error_msg)
#         continue
#
#     inp_day = input("Введите день: ")
#     inp_day_schedule = inp_class_schedule.get(inp_day, -1)
#
#     if inp_day_schedule == -1:
#         print(error_msg)
#         continue
#
#     print("\n".join(inp_day_schedule))


