from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from bson.json_util import dumps
import uuid

loginList = list()
loginMap = dict()
address = '127.0.0.1'

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://lab2:ssHIbMqjtPAEGCLf@cluster0-moytw.mongodb.net/airline1?retryWrites=true'
mongo = PyMongo(app)

def add_new_user(username, password, name):
    if mongo.db.customers.find_one({"userID": username}):
        return False
    else:
        mongo.db.customers.insert_one({"customerName": name, "userID": username, "password": password})
        return True
    return False

def valid_user(username,password):
    if mongo.db.customers.find_one({"userID": username}):
        if mongo.db.customers.find_one({"userID": username})['password'] == password:
            return True
    return False

def createReservation(fromLoc,toLoc,date,userID):
    tempRevID = str(uuid.uuid4())
    while mongo.db.reservations.find_one({"revID": tempRevID}):
        tempRevID = str(uuid.uuid4())
    mongo.db.reservations.insert_one({"from": fromLoc, "to": toLoc, "date": date,"customer":userID, "revID":tempRevID})

def getReservations(username):
    listToReturn = []
    for reserv in mongo.db.reservations.find({"customer": username}):
        listToReturn.append(reserv)
    print(listToReturn)
    return listToReturn

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/index.html')
def index():
    return render_template("index.html")

@app.route('/reservation.html')
def reservation():
    if request.remote_addr in loginList:
        return render_template("reservation.html")
    else:
        return redirect("http://" + address + ":5000/login", code=302)

@app.route('/book.html', methods=['GET', 'POST'])
def book():
    error = None
    if request.remote_addr in loginList:
        if request.method == 'POST':
            fromLoc = request.form['from']
            toLoc = request.form['to']
            month = request.form['month']
            day = request.form['day']
            year = request.form['year']
            date = month + '/' + day + '/' + year
            createReservation(fromLoc,toLoc,date,loginMap[request.remote_addr])
            return redirect("http://" + address + ":5000/reservation.html", code=302)
    else:
        return redirect("http://" + address + ":5000/login", code=302)
    return render_template('book.html', error=error)


@app.route('/partners.html')
def partners():
    return render_template("partners.html")

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    if request.method == 'POST':
        add_new_user(request.form['username'], request.form['password'],request.form['name'])
        return redirect("http://" + address + ":5000/login", code=302)
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_user(request.form['username'], request.form['password']):
            global loginList
            global loginMap
            loginMap[request.remote_addr] = request.form['username']
            loginList.append(request.remote_addr)
            global currentUser
            currentUser = request.form['username']
        else:
            error = 'Invalid Credentials. Please try again.'
        return redirect("http://" + address + ":5000/", code=302)
    return render_template('login.html', error=error)

@app.route('/getUserName')
def getUserName():
    return ""

@app.route('/changeAirline', methods=['GET', 'POST'])
def changeAirline():
    pass

@app.route('/returnReservations', methods=['GET', 'POST'])
def returnReservations():
    reservationsToReturn = getReservations(loginMap[request.remote_addr])
    return dumps(reservationsToReturn)

if __name__ == '__main__':
    app.run()