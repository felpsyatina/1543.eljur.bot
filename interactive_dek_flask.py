from flask import Flask, render_template, request
from lessons_db_manip import LessonDbReq
import functions

app = Flask(__name__)


def short_name(string):
    arr = string.split()
    for i in range(1, len(arr)):
        arr[i] = arr[i][0] + '.'
    return " ".join(arr)


@app.route('/desk')
def display():
    req = LessonDbReq()
    lesson_number = request.args.to_dict()
    lessons = req.get_beautified_lessons_for_desk(**lesson_number)
    for lesson in lessons:
        lesson['teacher_short'] = short_name(lesson['teacher'])
    new_lessons = {}
    for class_name in functions.classes:
        new_lessons[class_name] = []
    for lesson in lessons:
        new_lessons[lesson['class_name']] += [lesson]
    new_lessons = sorted(new_lessons.items(), key=lambda x: int(x[0][:-1]))

    return render_template('desk.html', lessons=new_lessons)


if __name__ == '__main__':
    app.run()
