import sqlite3

class Parser:

    """
        class Parser:
            Этот класс содержит в себе методы create_query(),
            get_jumoreski() и get_random()
            Они позволяют парсить json и выдавать список юморесок по поиску
    """

    def __init__(self):
        self.query = 'SELECT og AS text, img_id AS img_id FROM main WHERE'
        self.db = sqlite3.connect("db/main_base.db")
        self.cursor = self.db.cursor()

    def create_query(self, string, amount=1, sort_by='popularity'):
        """
            def create_query(self, string, amount, sort_by) -> string
                Метод получает строку с частью url и конвертирует ее в запрос SQL
        """
        queries = string.split('&')
        for i in queries:
            if 'contains_img' in i and '1' in i:
                self.query += ' main.img_id != 0 AND' 
            elif 'contains_img' in i:
                self.query += ' main.img_id == 0 AND' 
            else:
                if 'amount' not in i and 'sort_by' not in i:
                    self.query += ' main.' + i + ' AND'
        self.query = self.query[:-4]
        self.query += ' order by main.' + sort_by + ' desc limit ' + amount
        print('SQL QUERY:', self.query)

    def get_jumoreski(self):
        """
            def get_jumoreski(self): -> list
                Метод берет self.query (запрос SQL), исполняет его и выводит
                список найденных юморесок
        """
        text = list(self.cursor.execute(self.query).fetchall())
        result = []
        for i in range(len(text)):
            img_query = """SELECT url FROM images WHERE id = {}""".format(text[i][1])    
            images = list(self.cursor.execute(img_query).fetchall())
            result.append((text[i][0].replace('\\n', '<br>'), images))
        print(result)
        self.db.close()
        return str(result)

    def get_random_from_query(self):
        """
            def get_random_from_query(self): -> string
                Метод берет self.query (запрос SQL), исполняет его и выводит
                случайную юмореску из списка
        """
        self.query += "ORDER BY RANDOM() LIMIT 1"
        result = list(self.cursor.execute(self.query).fetchall())
        self.db.close()
        return result

    def get_random(self):
        """
            def get_random(self): -> string
            Метод возвращает случайную юмореску из базы 
        """
        text_query = """SELECT og AS text, img_id AS img_id FROM main 
                        WHERE main.swears = 0 and main.thread = 0 and main.img_id = 0 
                        ORDER BY RANDOM() LIMIT 1"""
        text = self.cursor.execute(text_query).fetchall()[0]
        img_query = """SELECT url FROM images WHERE id = {}""".format(text[1])
        img = self.cursor.execute(img_query).fetchall()
        self.db.close()
        result = (text[0].replace('\\n', '<br>'), img)
        print('RESULT:', result)
        return result
