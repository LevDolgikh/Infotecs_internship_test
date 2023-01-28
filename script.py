from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import json

import sqlite3 as sql

import string

HOST_NAME = "127.0.0.1"
SERVER_PORT = 8000
FILE_PATH = "RU.txt"
PATH_TO_DB = "GeoDB.db"
TABLE_NAME = "cities"
WEB_CLIENT_PATH = "/webclient"
OTHER_CLIENT_PATH = "/otherclient"

class GeoTableDB:
    """Класс для работы с базой данных

    При инициализации просто создается объект класса с указанием путей до базы данных, файла с информацией и таблицы.

    Описание методов:

    метод createDB создает базу данных вида sqlite3 по пути pathToDB = 'GeoDB.db', извлекая данные из pathToData = 'RU.txt'
    таблица с названиями городов находиться в базе данных называется tableName = 'cities'

    getDataFromTxt(geoid) - извлекает информацию о городе по geoID в формате sqlite3.Row

    getCityInfoById(page, count) - извлекает страницу (page) с информацией о городах в количесте (count) в виде листа sqlite3.Row

    getTwoCitiesByRussianName(cityName1, cityName2) - по русским именам находит соотвествующие города с наибольшим населением 
    выдает (sqlite3.Row, sqlite3.Row)"""
    
    def __init__(self, pathToData = "RU.txt", pathToDB = "GeoDB.db", tableName = "cities"):
        """Инициальзация базового объекта базы данных"""
        self.pathToData = pathToData
        self.pathToDB = pathToDB
        self.tableName = tableName

    def createDB(self):
        """Извлечение данных из файла и помещение их в базу данных"""
        con = sql.connect(self.pathToDB)
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS " + str(self.tableName))
        createTableCommand = "CREATE TABLE " + self.tableName + " "
        createTableCommand += """(
                                geonameid INTEGER NOT NULL,
                                name TEXT,
                                asciiname TEXT,
                                alternatenames TEXT,
                                latitude REAL,
                                longitude REAL,
                                feature_class TEXT,
                                feature_code TEXT,
                                country_code TEXT,
                                cc2 TEXT,
                                admin1_code TEXT,
                                admin2_code TEXT,
                                admin3_code TEXT,
                                admin4_code TEXT,
                                population INTEGER,
                                elevation INTEGER,
                                dem INTEGER,
                                timezone TEXT,
                                modification_date TEXT
                            );"""
        cur.execute(createTableCommand)

        command = "INSERT INTO " + self.tableName + " "
        command += "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data = self.getDataFromTxt(self.pathToData)
        cur.executemany(command, data) 
        con.commit()
        cur.close()
        con.close()

    def getDataFromTxt(self, pathToFile):
        """Метод извлечения данных из файла"""
        data = []

        file = open(pathToFile, 'r', encoding='utf-8')

        read = True
        while read:
            row = file.readline()
            if row:
                rowInList = row[:-1].split('\t')
                data.append(rowInList)
            else:
               read = False 

        file.close()
        return data
    
    def getCityInfoById(self, geoid):
        """Получение информации о городе по его ID"""
        con = sql.connect(self.pathToDB)
        con.row_factory = sql.Row

        cur = con.cursor()
        cityInfo = cur.execute("SELECT * FROM cities WHERE geonameid=" + str(geoid)).fetchone()

        cur.close()
        con.close()

        return cityInfo

    def getCitiesByPageAndCount(self, page, count):
        """Получить нескольких городов с указанной страницы"""
        con = sql.connect(self.pathToDB)
        con.row_factory = sql.Row

        cur = con.cursor()
        offset = page*count
        citiesOnPage = cur.execute("SELECT * FROM cities WHERE feature_code LIKE 'PP%' LIMIT " + str(offset) + "," + str(count)).fetchall()

        cur.close()
        con.close()

        return citiesOnPage

    def getTwoCitiesByRussianName(self, cityName1, cityName2):
        """Выборка городов по их названиям"""
        con = sql.connect(self.pathToDB)
        con.row_factory = sql.Row

        cur = con.cursor()
        command1 = "SELECT * FROM cities WHERE "
        command1 += "alternatenames LIKE '%" + str(cityName1) + "%' AND feature_code LIKE 'PP%' ORDER BY population DESC"
        command2 = "SELECT * FROM cities WHERE "
        command2 += "alternatenames LIKE '%" + str(cityName2) + "%' AND feature_code LIKE 'PP%' ORDER BY population DESC"
        city1Info = cur.execute(command1).fetchone()
        city2Info = cur.execute(command2).fetchone()
        if city1Info and city2Info:
            citiesByName = (city1Info, city2Info)
        else:
            citiesByName = None
        cur.close()
        con.close()
        
        return citiesByName

def generateIndexPage(webClientPath, otherClientPath):
    """Генерация главной HTML-страницы сайта"""
    res = """<html><head><title>Main Page</title><meta content='text/html; charset=UTF-8' http-equiv='Content-Type'></head>
            <body>
            <p>Работа с сервером может осуществляться с помощью веб-клиента и мануально.</p>
            <p>Для использования веб-клиента используйте <a href = '%s'> %s </a>. </p>
            <p>Для отправки запросов вручную используйте <a href = '%s'> %s </a> и инструкцию readme. </p>
            </body></html>""" % (WEB_CLIENT_PATH, WEB_CLIENT_PATH, OTHER_CLIENT_PATH, OTHER_CLIENT_PATH)
    return res

def generateWebClientInterface():
    """Генерация страницы помогающая пользователю искать информацию"""
    res = """<html><head><title>Web client page</title><meta content='text/html; charset=UTF-8' http-equiv='Content-Type'></head>
            <body>
            <p>Вам доступно 3 метода поиска: поиск по ID, выкладка по городам с какой-то страницы и поиск двух городов по русским названиям с их сравнением</p>
            <h2>Поиск по ID</h2>
            <form name="findById" method="get" action="%s/Method1">
            <div>
                <label for="geonameid">Номер записи:</label>
                <input name="geonameid" id="geonameid" value="1489425"  type="number" required/>
            </div>
            <div>
                <button>Поиск</button>
            </div>
            </form>
            <h2>Поиск по странице и количеству записей</h2>
            <form name="findByPageAndCount" method="get" action="%s/Method2">
            <div>
                <label for="count">Количество записей на страницу:</label>
                <input name="count" id="count" value="10"  type="number" min="1" required/>
            </div>
            <div>
                <label for="page">Номер страницы:</label>
                <input name="page" id="page" value="1"  type="number" min="1" required/>
            </div>
            <div>
                <button>Поиск</button>
            </div>
            </form>
            <h2>Поиск по русским названиям</h2>
            <form name="findByPageAndCount" method="get" action="%s/Method3">
            <div>
                <label for="city1">Первый город:</label>
                <input name="city1" id="city1" value="Томск"  type="text" required/>
            </div>
            <div>
                <label for="city2">Второй город:</label>
                <input name="city2" id="city2" value="Северск"  type="text" required/>
            </div>
            <div>
                <button>Поиск</button>
            </div>
            </form>
            </body></html>""" % (WEB_CLIENT_PATH, WEB_CLIENT_PATH, WEB_CLIENT_PATH)

    return res

def generateOneCityInformationPage(geonameid, sqliteRow):
    """Генерация страницы информации об одном городе (населенном пункте)"""
    res = """<html><head><title>Search result</title><meta content='text/html; charset=UTF-8' http-equiv='Content-Type'></head>
        <body>
        <h2>Результат поиска по ID %s</h2>
        <table cellspacing="2" border="1" cellpadding="5">""" % (geonameid)
    res += "<tr>"
    for key in sqliteRow.keys():
        res += "<th>" + str(key) + "</th>"
    res += "</tr>"
    res += "<tr>"
    for item in sqliteRow:
        res += "<td>" + str(item) + "</td>"
    res += "</tr>"
    res += "</table>"
    res += "<p><a href = '..%s'> вернуться назад</a></p>" %(WEB_CLIENT_PATH)
    res += "</body></html>"

    return res

def generateCitiesInformationPage(page, count, sqliteRowList):
    """Генерация страницы с информацией о нескольких городах (населенных пунктах)"""
    res = """<html><head><title>Search result</title><meta content='text/html; charset=UTF-8' http-equiv='Content-Type'></head>
        <body>
        <h2>Результат поиска по количеству элементов на странице %s, номер страницы %s </h2>
        <table cellspacing="2" border="1" cellpadding="5">""" % (count, page)
    res += "<tr>"
    for key in sqliteRowList[0].keys():
        res += "<th>" + str(key) + "</th>"
    res += "</tr>"
    for row in sqliteRowList:
        res += "<tr>"
        for item in row:
            res += "<td>" + str(item) + "</td>"
        res += "</tr>"
    res += "</table>"
    res += "<p><a href = '..%s'> вернуться назад</a></p>" %(WEB_CLIENT_PATH)
    res += "</body></html>"

    return res

def generateCitiesComparisonPage(city1Name, city2Name, sqliteRowList, northernCityName, sameTimeZone):
    """Генерация страницы для сравнения двух городов"""
    res = """<html><head><title>Search result</title><meta content='text/html; charset=UTF-8' http-equiv='Content-Type'></head>
        <body>
        <h2>Результат поиска названиям двух городов %s и %s </h2>
        <table cellspacing="2" border="1" cellpadding="5">""" % (city1Name, city2Name)
    res += "<tr>"
    for key in sqliteRowList[0].keys():
        res += "<th>" + str(key) + "</th>"
    res += "</tr>"
    for row in sqliteRowList:
        res += "<tr>"
        for item in row:
            res += "<td>" + str(item) + "</td>"
        res += "</tr>"
    res += "</table>"
    res += "<p>Более северный город: " + str(northernCityName) + "</p>"
    if sameTimeZone:
        res += "<p>Одинаковый ли часовой пояс: да</p>"
    else:
        res += "<p>Одинаковый ли часовой пояс: нет</p>"
    res += "<p><a href = '..%s'> вернуться назад</a></p>" %(WEB_CLIENT_PATH)
    res += "</body></html>"

    return res

def generateNotEnoughDataPage():
    """Генерация страницы при неверном запросе"""
    res = """<html><head><title>Search result</title><meta content='text/html; charset=UTF-8' http-equiv='Content-Type'></head>
        <body>
        <h2>Неверный запрос или по запрашиваемым данных нет результатов, <a href = '..%s'> вернуться назад</a></h2>
        <table cellspacing="2" border="1" cellpadding="5">""" %(WEB_CLIENT_PATH)
    res += "</body></html>"

    return res
            
class MyServer(BaseHTTPRequestHandler):
    """Класс обработки запросов на сервер"""
    def do_GET(self):
        """Обработка GET-запросов"""
        path = urlparse(self.path).path
        query_components = parse_qs(urlparse(self.path).query)

        if path == "/":
            self.showIndexPage()
        elif path == WEB_CLIENT_PATH:
            self.showWebClientPage()
        elif path == (WEB_CLIENT_PATH + "/Method1"):
            geonameid = self.extractFromQuery(query_components, {'geonameid': 'int'})
            if geonameid:
                self.processMethod1(geonameid)
        elif path == (WEB_CLIENT_PATH + "/Method2"):
            page, count = self.extractFromQuery(query_components, {'page':'int', 'count':'int'})
            if page and count:
                self.processMethod2(page, count)
        elif path == (WEB_CLIENT_PATH + "/Method3"):
            city1Name, city2Name = self.extractFromQuery(query_components, {'city1':'text', 'city2':'text'})
            if city1Name and city2Name:
                self.processMethod3(city1Name, city2Name)
        elif path == "/":
            self.showIndexPage()

    def do_POST(self):
        """Обработка POST-запросов"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data)
        if self.path == OTHER_CLIENT_PATH:
            methodId = message.get('methodId')
            if methodId == 1:
                geonameid = message.get('geonameid')
                if geonameid:
                    self.processMethod1(geonameid, mode="JSON")
                else:
                    self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))
            elif methodId == 2:
                page = message.get('page')
                count = message.get('count')
                if page and count :
                    self.processMethod2(page, count, mode="JSON")
                else:
                    self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))
            elif methodId == 3:
                city1 = message.get('city1')
                city2 = message.get('city2')
                if city1 and city2 :
                    self.processMethod3(city1, city2, mode="JSON")
                else:
                    self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))
            else:
                self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))
        else:
            self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))

    def extractFromQuery(self, query_components, itemsToExtract):
        """Query парсер"""
        components = []

        for key in itemsToExtract.keys():
            componentType = itemsToExtract.get(key)
            component = query_components.get(key)
            if component:
                component = component[0]
                if componentType == 'int':
                    component = int(component)
                else:
                    component = str(component)
                    component.translate(str.maketrans('', '', string.punctuation))
                components.append(component)
            else:
                self.send_error(400, "Bad Request", "Query can't be parsed")
                return None
        
        if len(components) == 1:
            return components[0]
        else:
            return tuple(components)

    def showIndexPage(self):
        """Метод отображения главной страницы"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(generateIndexPage(WEB_CLIENT_PATH, OTHER_CLIENT_PATH), "utf-8"))

    def showWebClientPage(self):
        """Метод отображения страницы с элементами поиска"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(generateWebClientInterface(), "utf-8"))

    def processMethod1(self, geonameid, mode = "HTML"):
        """Вывод информации о городе по geonameid"""
        geoTableDB = GeoTableDB(FILE_PATH, PATH_TO_DB, TABLE_NAME)
        cityInfo = geoTableDB.getCityInfoById(geonameid)
        if mode == "HTML":
            if cityInfo:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(generateOneCityInformationPage(geonameid, cityInfo), "utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(generateNotEnoughDataPage(), "utf-8"))
        elif mode == "JSON":
            if cityInfo:
                keys = cityInfo.keys()
                values = tuple(cityInfo)
                self.wfile.write(bytes(json.dumps({'keys': keys, 'values' : values}), "utf-8"))
            else:
                self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))


    def processMethod2(self, page, count, mode = "HTML"):
        """Вывод информации о нескольких города помещающихся на одной странице"""
        geoTableDB = GeoTableDB(FILE_PATH, PATH_TO_DB, TABLE_NAME)
        citiesInfo = geoTableDB.getCitiesByPageAndCount(page, count)

        if mode == "HTML":
            if citiesInfo:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(generateCitiesInformationPage(page, count, citiesInfo), "utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(generateNotEnoughDataPage(), "utf-8"))
        elif mode == "JSON":
            if citiesInfo:
                keys = citiesInfo[0].keys()
                valuesList = []
                for values in citiesInfo:
                    valuesList.append(list(tuple(values)))
                self.wfile.write(bytes(json.dumps({'keys': keys, 'values' : valuesList}), "utf-8"))
            else:
                self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))


    def processMethod3(self, cityName1, cityName2, mode = "HTML"):
        """Сравнение двух городов"""
        geoTableDB = GeoTableDB(FILE_PATH, PATH_TO_DB, TABLE_NAME)
        citiesInfo = geoTableDB.getTwoCitiesByRussianName(cityName1, cityName2)
        if mode == "HTML":
            if citiesInfo:
                northernCityName = citiesInfo[0]['name']
                if citiesInfo[0]['latitude'] < citiesInfo[1]['latitude']:
                    northernCityName = citiesInfo[1]['name']
                sameTimeZone = citiesInfo[0]['timezone'] == citiesInfo[1]['timezone']
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(generateCitiesComparisonPage(cityName1, cityName2, citiesInfo, northernCityName, sameTimeZone), "utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(generateNotEnoughDataPage(), "utf-8"))
        elif mode == "JSON":
            if citiesInfo:
                northernCityName = citiesInfo[0]['name']
                if citiesInfo[0]['latitude'] < citiesInfo[1]['latitude']:
                    northernCityName = citiesInfo[1]['name']
                sameTimeZone = citiesInfo[0]['timezone'] == citiesInfo[1]['timezone']
                keys = citiesInfo[0].keys()
                valuesList = []
                for values in citiesInfo:
                    valuesList.append(list(tuple(values)))
                self.wfile.write(bytes(json.dumps({'keys': keys, 'values' : valuesList, 
                'northernCityName' : northernCityName, 'sameTimeZone' : sameTimeZone}), "utf-8"))
            else:
                self.wfile.write(bytes(json.dumps({'error': 'bad request'}), "utf-8"))

if __name__ == "__main__":
    """Запуск сервера"""
    geoTable = GeoTableDB(FILE_PATH, PATH_TO_DB, TABLE_NAME)
    geoTable.createDB()
    print("Database is created at " + str(PATH_TO_DB))

    webServer = HTTPServer((HOST_NAME, SERVER_PORT), MyServer)

    print("Server started http://%s:%s" % (HOST_NAME, SERVER_PORT))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")