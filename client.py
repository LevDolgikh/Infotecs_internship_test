import http.client
import json

HOST_NAME = "127.0.0.1"
SERVER_PORT = 8000
OTHER_CLIENT_WEB_PAGE = "/otherclient"

def method1POST(connection, geoid):

    headers = {'Content-type': 'application/json'}
    geonameid = {'methodId': 1, 'geonameid': geoid}

    json_data = json.dumps(geonameid)

    connection.request('POST', OTHER_CLIENT_WEB_PAGE, json_data, headers)

    response = connection.getresponse()
    json_responce = json.loads(response.read().decode())

    return json_responce

def method2POST(connection, page, count):

    headers = {'Content-type': 'application/json'}
    geonameid = {'methodId': 2, 'page': page, 'count' : count}

    json_data = json.dumps(geonameid)

    connection.request('POST', OTHER_CLIENT_WEB_PAGE, json_data, headers)

    response = connection.getresponse()
    json_responce = json.loads(response.read().decode())
    
    return json_responce

def method3POST(connection, city1, city2):

    headers = {'Content-type': 'application/json'}
    geonameid = {'methodId': 3, 'city1': city1, 'city2' : city2}

    json_data = json.dumps(geonameid)

    connection.request('POST', OTHER_CLIENT_WEB_PAGE, json_data, headers)

    response = connection.getresponse()
    json_responce = json.loads(response.read().decode())
    
    return json_responce

if __name__ == "__main__":

    conn = http.client.HTTPConnection(HOST_NAME, SERVER_PORT, timeout=10)
    # method1GET(connection, geoid = 451751)
    method1response = method1POST(connection = conn, geoid = 5)
    print("method1response", method1response)
    # method2response = method2POST(connection = conn, page = 1, count = 3)
    # print("method2response", method2response)
    # method3response = method3POST(connection = conn, city1 = "Томск", city2 = "Северск")
    # print("method3response", method3response)

    

