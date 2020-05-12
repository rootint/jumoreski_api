import sqlite3 as sql  # для работы с базами данных
import datetime as dt  # для вычисления дат постов
from os import chdir, remove  # для смены рабочей папки и удаления файла
from time import sleep as wait  # для прогрузки страницы
from selenium import webdriver  # для работы с браузером
from selenium.webdriver.chrome.options import Options  # для настройки браузера


# Эту часть выполнил Алексеев Вячеслав


class Downloader:
    '''Класс, созданный для загрузки постов в БД'''

    def __init__(self):
        chdir('./download')  # Перемещение в папку с программой
        options = Options()
        options.headless = True
        options.add_argument('log-level=3')
        self.WEB = webdriver.Chrome(options=options)  # Создание объекта, дающего доступ в Интернет
        temp = open('./temporary.txt', 'xb')  # Получение корней мата
        temp.write(bytes([255 - int(elem) for elem in open('./secret', 'rb').read()]))
        # Корни мата закодированы, чтобы в работе матные корни не были легко находимы и явны
        temp.close()  # Раскодировка файла
        self.swears = open('./temporary.txt', 'r', encoding='utf-8').read().split(', ')  # Корни в списке
        remove('./temporary.txt')  # Удаления файла с раскодированным текстом

    def processing(self, text):
        '''Обработка текста: преобразование переноса на следующую строку, эмоджи и ссылок'''

        text = text.replace('<br>', '\n').replace('</span>', '').replace('<a class="wall_post_more" onclick="hide(this, domPS(this)); show(domNS(this));">Показать полностью…</a><span style="display: none">', '')
        # Преобразование переноса на следующую строку и удаление лишнего HTML-кода
        while '<img' in text:  # Преобразование эмоджи
            lbid = text.find('<img')
            rbid = text[lbid:].find('">') + lbid + 2
            emid = text[lbid:].find('alt') + lbid + 5
            text = text[:lbid] + text[emid] + text[rbid:]
        while '<a' in text:  # Преобразование ссылок
            text = text.replace(text[text.find('<a'):text.find('</a>') + 4], '\n<link> ' + text[text.find('">') + 2:text.find('</a>')] + '\n')
        return text.replace('"', "'")  # Замена всех ковычек на единичные, ведь при записи в таблицу двойные используются как код

    def to_key_words(self, text):
        '''Обработка текста: преобразование его в текст для ключевых слов (нет занков препинания, все слова написаны маленькими буквами)'''

        res = []
        for line in text.split('\n'):
            if not line.startswith('<link>'):  # Удаление знаков препинания
                line = line.lower().replace(',', ' ').replace('-', ' ').replace('—', ' ').replace('.', ' ').replace('!', ' ').replace('?', ' ').replace('(', ' ').replace(')', ' ').replace('/', ' ').replace('\\', ' ').replace(':', ' ').replace(';', ' ').replace('\'', ' ').replace('"', ' ')
                while '  ' in line:  # Сокращение лишних пробелов
                    line = line.replace('  ', ' ')
            else:  # Сохранение вида ссылок
                line = line[7:]
            res.append(line)  # Работает по линии
        res = '\n'.join(res)
        while '\n\n' in res:  # Сокращение лишних переносов
            res = res.replace('\n\n', '\n')
        return res.strip('\n')

    def rid_of_link(self, text):
        '''Обработка текста: преобразование текста с тэгами в начале строки "<link>",
        которые не позволяют при обработке текста в ключевые слова убирать знаки препинания из ссылок'''

        res = []
        skip = False
        for line in text.split('\n'):
            if skip:
                skip = False
                continue
            if line.startswith('<link>'):
                res = res[:-1]
                skip = True  # Стирание тэга
                line = line[7:]
            res.append(line)  # Работает по линии
        return '\n'.join(res)

    def run(self):
        '''Запуск работы объекта'''

        self.db_upload()

    def db_upload(self):
        '''Основная часть - скачивание информации, её преобразование и загрузка в БД'''

        db_ = sql.connect('../jumoreski.db')  # Переменная БД
        i, db, self.img_id = 0, db_.cursor(), 1  # Переменные страницы, курсора БД и ID для изображений
        while True:  # "Бесконечный" цикл
            self.WEB.get('https://vk.com/wall-92876084?offset=' + str(i * 20) + '&own=1')  # Переход на страницу
            wait(0.1)  # Ожидание прогрузки страницы
            if (i * 20) % 1000 == 0:
                db_.commit()  # Резервное копирование каждые 5000 постов
                file = open('./save-log.txt', 'w')
                file.write('Last saved on: ' + str(i * 20))
                file.close()  # Сохраняет номер последнего закомиченного поста
                print('Last saved on: ' + str(i * 20))
            posts = self.WEB.find_element_by_id('page_wall_posts').get_attribute('innerHTML').split('<div id="post-92876084_')[1:]
            if posts == []:  # Получение постов со страницу (сверху)
                break  # Если постов на странице нет, то мы дошли до конца
            for elem in posts:  # Перечисление постов
                if 'reply' in elem[:25]:  # Пропуск комментариев
                    continue  # Комментарии считаются за пост, однако они не нужны

                link = 'https://vk.com/wall-92876084_' + elem[:elem.find('"')]  # Ссылка

                if 'wall_post_text' not in elem:
                    text = '--'  # Если нет текста в посту
                    edited = '--'
                    length = 0
                else:
                    if 'class="wall_post_text"' in elem:
                        raw = elem[elem.find('class="wall_post_text"') + 23:]
                    else:  # Получение текста в "сыром" виде
                        raw = elem[elem.find('class="wall_post_text zoom_text"') + 33:]
                    raw = self.processing(raw[:raw.find('</div>')])  # "Переработка" текста
                    text = self.rid_of_link(raw)  # "Чистый" текст
                    length = len(text)
                    text = text.replace('\n', '\\n')  # Замена переноса строки (При загрузке в БД переном теряется)
                    edited = self.to_key_words(raw).replace('\n', '\\n')  # Текст ключевых слов
                
                # Для всех булевых значений используются 0 или 1, ведь так просит формат SQL
                swears = 0  # Сначала считается, что мата нет
                temp = edited.replace('ё', "е")  # Меняем в тексте с ключевыми словами "ё" на "е"
                for swear in self.swears:  # Прохожим по корням
                    if swear in temp:  # Если есть корень, то
                        swears = 1  # Есть мат в посте
                        break  # Если мат уже есть, то проверять на наличие мата далее не обязательно

                img_links = []  # Ссылки на изображения
                if 'page_post_sized_thumbs' in elem:  # Если есть изображения
                    photos = elem[elem.find('<a onclick="return showPhoto'):]
                    photos = photos[:photos.find('</div>')]  # Получения кода с изображениями
                    while True:
                        end = photos.find('/a>') + 3
                        if end == 2:
                            break  # Больше изображений нет
                        img_pos = photos.find('&quot;z&quot;:&quot;')
                        if img_pos == -1:  # Получение ссылки
                            img_pos = photos.find('&quot;y&quot;:&quot;')
                        if img_pos == -1:  # (Ссылки бывают в разном виде)
                            img_pos = photos.find('&quot;x&quot;:&quot;')
                        if img_pos == -1:  # На случай ошибки
                            raise Exception('Исключение в изображениях')
                        temp = photos[img_pos + 20:]
                        temp = temp[:temp.find('&quot;')].replace('\\/', '/')
                        img_links.append(temp)  # Пополнение листа с ссылками
                        photos = photos[end:]  # Переход на следующий элемент
                    img_id = self.img_id
                    self.img_id += 1  # Повышение ID на ссылки изображений
                else:
                    img_id = 0  # ID 0 приводит к значению "none", то есть нет изображения
                # Для изображений даётся ID, ведь в одном посте может быть несколько изображений
                # Однако списки в БД загрузить нельзя, поэтому приходится брать отдельную таблицу
                # В ней у каждой ссылки есть свой ID, приводящий к своему посту в основной таблице

                thread = 0  # Есть ли тред
                if 'class="copy_author"' in elem:
                    name = elem[elem.find('class="copy_author"'):]
                    name = name[:name.find('</a>')]
                    name = name[name.rfind('">') + 2:]
                    if name == 'ТРЕДШОТ':  # Если репост - это ТРЕДШОТ, то загрузка
                        thread = 1
                    else:  # Если репост любого другого паблика - пост пропускается
                        continue

                if 'abs_time' in elem:  # Первый вид выражения времени
                    date = elem[elem.find('abs_time') + 10:]
                    date = date[:date.find('"')]
                    if 'сегодня' in date:  # Обычно относится только к сегодняшним постам
                        date = list(map(int, date.split('в ')[1].split(':')))  # Обработка и преобразование в datetime и после в timestamp
                        date = dt.datetime.combine(dt.date.today(), dt.datetime.min.time()) + dt.timedelta(hours=date[0], minutes=date[1])
                    else:  # Если относится не к сегодняшним постам - ошибка
                        raise Exception('Исключение в datetime - abs_time')
                else:  # Второй вид
                    date = elem[elem.find('class="rel_date">') + 17:]
                    date = date[:date.find('</span>')]
                    if 'сегодня' in date:  # Для сегодняшних постов
                        date = list(map(int, date.split('в ')[1].split(':')))  # Обработка и преобразование в datetime и после в timestamp
                        date = dt.datetime.combine(dt.date.today(), dt.datetime.min.time()) + dt.timedelta(hours=date[0], minutes=date[1])
                    elif 'вчера' in date:  # Для вчерашних постов
                        date = list(map(int, date.split('в ')[1].split(':')))  # Обработка и преобразование в datetime и после в timestamp
                        date = dt.datetime.combine(dt.date.today() - dt.timedelta(days=1), dt.datetime.min.time()) + dt.timedelta(hours=date[0], minutes=date[1])
                    elif ' в ' in date:  # Для постов этого года (не сегодняшних и не вчерашних)
                        date = date.split()[:2] + date.split()[3].split(':')  # Обработка и преобразование в datetime и после в timestamp
                        date[1] = {'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6, 'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12}[date[1]]
                        date = dt.datetime(dt.date.today().year, date[1], int(date[0]), int(date[2]), int(date[3]))
                    else:  # Для постов прошлых лет
                        date = date.split()  # Обработка и преобразование в datetime и после в timestamp
                        date[1] = {'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6, 'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12}[date[1]]
                        date = dt.datetime(int(date[2]), date[1], int(date[0]))
                date += dt.timedelta(hours=2)  # Время получается московское, для удобства проверки переведно в пермское
                date = date.timestamp()  # Получения числа (timestamp) из объекта datetime

                try:  # Получение просмотров поста
                    views = elem[elem.find('Likes.updateViews(\'wall-92876084'):]
                    views = views[views.find('data-count="'):]  # Получение и обработка
                    views = float(views[:views.find('K')]) * 1000  # У постов написано количество просмотров в "К" (тыс.)
                except ValueError:  # До 2017 года просмотры на постах не cчитывались
                    views = 8500  # Популярность вычислять всё равно надо, поэтому используется примерное среднее значение

                likes = elem[elem.find('onmouseover="Likes.showLikes(this'):]  # Лайки
                likes = likes[likes.find('data-count="') + 12:]  # Получение и обработка
                likes = float(likes[:likes.find('"')])

                reps = elem[elem.find('onmouseover="Likes.showShare(this'):]  # Репосты
                reps = reps[reps.find('data-count="') + 12:]  # Получение и обработка
                reps = float(reps[:reps.find('"')])

                popularity = (likes / 100 + reps) / views * 100  # Популярность
                # Формула популярности выведена нами
                # Чем больше просмотревших пост людей, которые оценили (лайк/репост) пост, тем он популярнее

                db.execute(f'''
                INSERT INTO main(og,edited,length,swears,link,img_id,thread,date,views,likes,reposts,popularity)
                VALUES ("{text}","{edited}",{length},{swears},"{link}",{img_id},{thread},{date},{int(views)},{int(likes)},{int(reps)},{popularity})''')
                # Загрузка в БД
                for elem in img_links:  # Загрузка ссылок изображений
                    db.execute(f'''
                    INSERT INTO images(id, url)
                    VALUES ({img_id}, "{elem}")''')
            i += 1  # Переход на след. страницу
        print('done')  # Оповещение о доходе до конца
        db_.commit()  # Коммит в БД
        print('uploaded')  # Оповещение о загрузке данных в БД, и конец программы


if __name__ == '__main__':  # Запускаемая часть кода
    downloader = Downloader()
    downloader.run()  # Запуск "загружателя"
