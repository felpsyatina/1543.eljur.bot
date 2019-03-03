ydates = {'июня': 5,
            'марта': 2,
            'февраля': 1,
            'январь': 0,
            'ноябрь': 10,
            'апрель': 3,
            'март': 2,
            'июль': 6,
            'ноября': 10,
            'января': 0,
            'декабря': 11,
            'июля': 6,
            'август': 7,
            'сентябрь': 8,
            'июнь': 5,
            'сентября': 8,
            'мая': 4,
            'апреля': 3,
            'августа': 7,
            'февраль': 1,
            'октября': 9,
            'май': 4,
            'октябрь': 9,
            'декабрь': 11}


parallels = {
    50: 5,
    49: 6,
    48: 7,
    47: 8,
    46: 9,
    45: 10,
    46: 11
}


quest = {'что': 'commands',
         'умеешь': 'commands',
         'команды': 'commands',
         'регистрация': 'registration',
         'зарегистрироваться': 'registration',
         'мой аккаунт': 'account',
         'мой акк': 'account',
         'акк': 'account',
         'расписание': 'schedule',
         'отмена': 'cancel',
         'замена': 'replacement',
         'комментарий': 'comment',
         'коментарий': 'comment',
         'коммент': 'comment',
         'комент': 'comment',
         'поддержка': 'support',
         'дз': 'hometask',
         'домашнее': 'hometask',
         'задание': 'hometask',
         'домашка': 'hometask'
         }


answers = {'/start': ["Привет, я ЭлжурБот. Чтобы узнать мои команды, напиши: 'Что ты умеешь?' или 'Команды' или воспользуйя кнопками."],
            'commands': ["Вот что я могу:\n"
                                          "Регистация -- советую начать с этой команды для дальнейшей работы со мной.\n"
                                          "Мой аккаунт/Мой акк -- расскажу, что знаю о тебе. Можешь изменить информацию о себе.\n"
                                          "Расписание на *дата* -- я скину расписание на указанную дату. Так же можешь написать: 'Расписание на неделю *дата*' и произойдет немыслимое!\n"
                                          "Отмена или Замена -- сообщить, что какой-то урок отменили/заменили.\n"
                                          "Комментарий/Коммент -- расскать, что думаешь о прошедшем уроке.\n"
                                          "Поддержка -- задать вопрос или сообщить об ошибке моим СОЗДАТЕЛЯМ.\n"
                                          "Пока что все. Я обзятельно тебе скажу, как только научусь чему-то новому!)"],
           'registration': ["Ура! Новый пользователь! Как мне тебя называть?",
                                                  #"Придумай пароль:",
                                                  #"Повтори пароль еще раз:"
                                                  "В каком классе учишься?",
                                                  "Хорошо, с необходимым закончили. Захочешь изменить или добавить данные -- напиши Мой аккаунт."],
           'account': ["Вот что я знаю о тебе:", "Данные о тебе:", "Твои данные:"],
           'schedule': ["Лови", "Скинул", "Вот"],
           'cancel': ["Какой урок отменен?", "Какого урока не будет?", "Что отменили?"],
           'replacement': ["Какой урок заменен?", "Что заменили?"],
           'comment': ["Какой урок хочешь прокомментировать?"],
           'support': ["Оу, надеюсь, что все в порядке) Твое сообщение поддержке:"]}


users_table_fields = ['_id',
                      'login',
                      'parallel',
                      'name',
                      'surname',
                      'access_level',
                      'ban',
                      'vk_login',
                      'vk_id',
                      'tele_login',
                      'tele_id',
                      'status',
                      'password_hash']
