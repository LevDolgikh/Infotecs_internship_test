### Запуск сервера
python script.py

### Используемые библиотеки
- http.server
- urllib
- json
- sqlite3
- string

### Описание файлов в проекте
1. client.py - пример обращения к серверу через клиента
2. GeoDb.db - автоматически создаваемая база данных
3. Razrabotchik-Python.docx - текст с заданием    
4. readme.txt - иструкция к файлу RU.txt с описанием городов и т.п.
5. RU.txt - описание городов
6. scripy.py - сервер, который считывает файл RU.txt и выводит информацию пользователя по нескольким вариантам запросов

### Особенности работы сервера
1. Сервер работает по адресу 127.0.0.1:8000/
2. Перед запуском сервера генерируется база данных GeoDB.db в папке со script.py

### Взаимодействие с сервером:
С сервером можно взаимодействовать 2-мя образами: через веб-интерфейс и отдельным клиентом отсылая POST-запросы

**Взаимодействие через веб-интерфейс**
1. Веб-интерфейс доступен по ссылке 127.0.0.1:8000/webclient
2. Веб-интерфейс помогает генерировать ссылки для получения страничек для GET-запросов
3. В соответствии с заданием реализованы 3 способа извлечения информации: по ID, по количеству элементов на страницу и номер страницы, вводя два русских города вывводиться информация о них и минимальное сравнение
4. Вручную обратиться к информации о населенном пункте по ID можно по ссылке: http://127.0.0.1:8000/webclient/Method1?geonameid=%ВАШ_ID%, где %ВАШ_ID% - заменить на интересующий ID
5. Вручную обратиться к информации по странице и количеству элементов можно по ссылке: http://127.0.0.1:8000/webclient/Method2?count=%КОЛ-ВО_ЭЛЕМЕНТОВ%&%СТРАНИЦА%=1, где %КОЛ-ВО_ЭЛЕМЕНТОВ% и %СТРАНИЦА% - заменить на интересующие значения
6. Вручную запросить информацию о двух городах можно по ссылке: http://127.0.0.1:8000/webclient/Method3?city1=%НАЗВАНИЕ_ГОРОДА1%&city2=%НАЗВАНИЕ_ГОРОДА2%, где %НАЗВАНИЕ_ГОРОДА1% и %НАЗВАНИЕ_ГОРОДА2%  - заменить на интересующие названия городов
7. В случае невозможности обработать запрос будет открываться страничка с ошибкой, проверьте, все ли вы ввели правильно
8. Оформление страничек "минималистичное", так как складывать все в один скрипт неудобно

**Взаимодействие сторонним клиентом**
1. С POST-запросами можно обращаться по адресу: http://127.0.0.1:8000/otherclient
2. По адресу из пункта (1) сервер принимает и отправляет информацию в виде JSON-словарей
3. Для получения информации о населенном пункте по ID необходимо отправить следующую информацию:     
```python
# methodId - применяемая обработка, geoid - ID, по которому хочется получить информацию
headers = {'Content-type': 'application/json'}
data = {'methodId': 1, 'geonameid': geoid}
json_data = json.dumps(data)
connection.request('POST', "/otherclient", json_data, headers)
```
```python
# Output example:
# JSON словарь содержащий ключи (название полей) и их значения для одного города, населенного пункта
{'keys': ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 'dem', 'timezone', 'modification_date'], 
 'values': [451751, 'Zhitnikovo', 'Zhitnikovo', '', 57.20064, 34.57831, 'P', 'PPL', 'RU', '', '77', '', '', '', 0, '', 198, 'Europe/Moscow', '2011-07-09']}
```
4. Для получения информации о нескольких городах по странице и количеству элементов необходимо отправить следующий запрос:
```python
# methodId - применяемая обработка 
# page - номер страницы
# count - количество элементов на страницу
headers = {'Content-type': 'application/json'}
data = {'methodId': 2, 'page': page, 'count' : count}
json_data = json.dumps(data)
connection.request('POST', "/otherclient", json_data, headers)
```
```python
# Output example:
# JSON словарь содержащий ключи (название полей) и их значения для нескольких городов, населенных пунктов
{'keys': ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 'dem', 'timezone', 'modification_date'], 
 'values': [[451750, 'Zhitovo', 'Zhitovo', '', 57.29693, 34.41848, 'P', 'PPL', 'RU', '', '77', '', '', '', 0, '', 247, 'Europe/Moscow', '2011-07-09'], 
            [451751, 'Zhitnikovo', 'Zhitnikovo', '', 57.20064, 34.57831, 'P', 'PPL', 'RU', '', '77', '', '', '', 0, '', 198, 'Europe/Moscow', '2011-07-09'], 
            [451752, 'Zhelezovo', 'Zhelezovo', '', 57.02591, 34.51886, 'P', 'PPL', 'RU', '', '77', '', '', '', 0, '', 192, 'Europe/Moscow', '2011-07-09']]}
```
5. Для получения информации о сравнение двух городов необходимо отправить следующий запрос:
```python
# methodId - применяемая обработка, 
# city1 - название первого города
# city2 - название второго города
headers = {'Content-type': 'application/json'}
data = {'methodId': 3, 'city1': city1, 'city2' : city2}
json_data = json.dumps(data)
connection.request('POST', "/otherclient", json_data, headers)
```
```python
# Output example:
# JSON словарь содержащий ключи (название полей) и их значения для нескольких городов, населенных пунктов. Также присутствует дополнительная информация согласно заданию
{'keys': ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 'dem', 'timezone', 'modification_date'], 
 'values': [[1489425, 'Tomsk', 'Tomsk', "TOF,Tom'sku,Tomck,Tomium,Toms'k,Tomsk,Tomska,Tomskaj,Tomskas,Tomszk,Tomçk,tomseukeu,tomska,tomusuku,tuo mu si ke,twmsk,twmsq,Τομσκ,Томск,Томскай,Томськ,Томьскъ,Տոմսկ,טומסק,تومسك,تومسک,ٹومسک,तोम्स्क,トムスク,托木斯克,톰스크", 56.49771, 84.97437, 'P', 'PPLA', 'RU', '', '75', '1489419', '', '', 574002, '', 117, 'Asia/Tomsk', '2022-10-16'], 
            [1538637, 'Seversk', 'Seversk', "Severs'k,Seversk,Severskas,Sewersk,Sewjersk,Siewiersk,Sèversk,Tomsk-7,sebeleuseukeu,sevuerusuku,swrsk,sywrsk,xie wei er si ke,Северск,Сєвєрськ,سورسک,سیورسک,セヴェルスク,謝韋爾斯克,세베르스크", 56.60056, 84.88639, 'P', 'PPL', 'RU', '', '75', '', '', '', 109844, '', 98, 'Asia/Tomsk', '2019-09-05']], 
 'northernCityName': 'Seversk', 
 'sameTimeZone': True}
```
6. При ошибке будет приходить следующий ответ:
```python
# Output example:
{'error': 'bad request'}
```
Это значит, что или запрос некорректен, или в базе данных недостаточно информации по запросу, например нету такого ID, города, двух городов для сравнения.

### Комментарии по заданию
Решение отсылаю весьма поспешно, так как на данный момент также работаю полный рабочий день и тратить много времени на выполнение сторонних заданий мне трудно. Скорее всего есть баги с запросами, HTML дизайн можно было бы улучшить, sql иньекции - думаю возможны.
Так как с REST API я до этого задания знаком не был, то реализовал 2 варианта обращения к серверу, так как из задания я не совсем понял что ожидается в качестве выходных данных.