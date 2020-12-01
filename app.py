import json

from flask import Flask, jsonify, request, render_template
import mysql.connector
import requests as req

app = Flask(__name__)

# ip di arduino, posto statico da routing
arduinoIp = "http://192.168.10.130"

myDb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "root",
    database = "sensorVisualizer"
)

myCursor = myDb.cursor()

@app.route('/')
def hello_world():
    #return jsonify({"about" : "anrto"})
    return render_template('index.html')

@app.route('/getValues', methods=['GET'])
def getValues():
    sqlQuery = "SELECT * FROM valuesTable"
    myCursor.execute(sqlQuery)
    row_headers = [x[0] for x in myCursor.description]
    result = myCursor.fetchall()
    json = []
    for x in result:
        json.append(dict(zip(row_headers, x)))
    print(result)
    #return jsonify(json)
    return dict(result)

@app.route('/resetAll', methods=['POST'])
def reloadTableDatabase():
    sqlQuery = "DELETE FROM valuesTable WHERE 1"
    myCursor.execute(sqlQuery)
    myDb.commit()
    return jsonify({"updated":"True"})

@app.route('/setValues', methods = ['POST'])
def setValue():
    reloadTableDatabase()
    jsonObj = request.get_json()
    print(jsonObj)
    for (k, v) in jsonObj.items():
        sqlQuery = "INSERT INTO valuesTable (sensorName, sensorValue) VALUES (%s, %s)"
        val = (k, v)
        myCursor.execute(sqlQuery, val)
        myDb.commit()
    return jsonify({"StatusCode":200,"InfoOperation":"set values to database","ResultOperation":"Correctly executed"})

@app.route('/changeStatesToOn/<int:sensor>', methods=['GET'])
def turnPinOn(sensor):
    #requests.get(arduinoIp + '/turnOn=' + sensor)
    req.get(arduinoIp + '/' + sensor.__str__() + '/on')
    format = "sensor " + sensor.__str__()
    return jsonify({format:"ON"})

@app.route('/changeStatesToOff/<int:sensor>', methods=['GET'])
def turnPinOff(sensor):
    req.get(arduinoIp + '/' + sensor.__str__() + '/off')
    format = "sensor" + sensor.__str__()
    return jsonify({format:"OFF"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
