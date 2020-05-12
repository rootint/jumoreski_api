import flask
from flask_restful import Api, Resource, reqparse
from data import db_session
import random
import json
import urllib3
from parser_class import Parser

class API(Resource):

    """
        class API(Resource):
            REST класс для получения юморесок
            Имеет только метод get(), так как менять базу данных пользователь не может
    """

    def __init__(self):
        self.parser = Parser()

    def get(self, query=''):
        """
            def get(self, query=''): -> string, int
                Метод, выполняющий GET-запрос, а именно получение юморесок по запросу
                Возвращает строку с ответом и код ответа
        """
        print('url:', query)
        s = query.split('&')
        sort_arg = 'popularity'
        for i in s:
            if 'amount' in i:
                amount = i[7:]
            if 'sort_by' in i:
                sort_arg = i[8:]
        if query != '' and 'amount' in query:
            self.parser.create_query(query, amount, sort_arg)
            result = json.dumps(self.parser.get_jumoreski(), ensure_ascii=False)
            return flask.make_response(result)
        elif query != '':
            self.parser.create_query(query, '1', sort_arg)
            result = json.dumps(self.parser.get_jumoreski(), ensure_ascii=False)
            return flask.make_response(result)
        else:
            result = self.parser.get_random()
            return flask.make_response(json.dumps(result, ensure_ascii=False))
        return 'you picked the wrong house fool', 404


http = urllib3.PoolManager()
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'slava_alekseev_molodec_1337'
api = Api(app)
api.add_resource(API, "/api", "/api/", "/api/<query>")


@app.route('/')
def index():
    param = {}
    request = http.request("GET", "http://localhost:1337/api").data.decode('utf-8')[1:]
    text_html = request.split('",')[0][1:] + '<br><br>'
    img_html = request.split('",')[1].split(',')
    for i in range(len(img_html)):
        if 'none' in img_html[i]:
            img_html[i] = ''
        if i != len(img_html) - 1:
            img_html[i] = '<img width=50% src=\"' + img_html[i][img_html[i].find('\"') + 1:-2] + '\"">'
        else:
            img_html[i] = '<img width=50% src=\"' + img_html[i][img_html[i].find('\"') + 1:-4] + '\"">'
    param['jumoreska'] = text_html + ''.join(img_html)
    return flask.render_template('index.html', **param)


@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/search')
def search():
    return flask.render_template('search.html')


@app.route('/search_result/<query>')
def search_result(query=""):
    param = {}
    request = http.request("GET", "http://localhost:1337/api/" + query).data.decode('utf-8')[1:] 
    print('ANSWER', request)
    if request != "[]\"":
        s = request[3:-3]
        result = []
        s = s.split(']), (')
        for i in range(len(s)):
            if i == 0:
                result.append(s[i].split(', ['))
            else:
                result.append(s[i].split(', ['))
                result[i][0] = result[i][0][1:-1]
            result[i][1] = result[i][1].split('), (')
            for j in range(len(result[i][1])):
                if len(result[i][1]) == 1:
                    result[i][1][j] = result[i][1][j][2:-3]
                else:
                    if j == 0:
                        result[i][1][j] = result[i][1][j][2:-2]
                    elif j == len(result[i][1]) - 1:
                        result[i][1][j] = result[i][1][j][1:-4]
                    else:
                        result[i][1][j] = result[i][1][j][1:-2]
            # print(*result[i][1])

        final_res = []
        for i in result:
            tmp = []
            tmp1 = []
            tmp.append(i[0] + '<br>')
            for j in i[1]:
                if 'none' not in j:
                    tmp1.append('<img src=\'' + j + '\'>')
            tmp.append(''.join(tmp1))
            final_res.append(''.join(tmp))
        param['amount'] = len(final_res)
        param['jumoreski'] = final_res
    else:
        param['amount'] = 1
        param['jumoreski'] = ['Юморески по результату поиска не найдены']
    return flask.render_template("search_result.html", **param)


def main():
    app.run(port=1337, host='127.0.0.1')


if __name__ == '__main__':
    main()