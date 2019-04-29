from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
import json

loginList = list()
loginMap = dict()
address = '127.0.0.1'

def add_new_user(username, password):
    count = 0
    return

def valid_user(username,password):
    return True

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://lab2:ssHIbMqjtPAEGCLf@cluster0-moytw.mongodb.net/airline1?retryWrites=true'
mongo = PyMongo(app)

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

@app.route('/partners.html')
def partners():
    return render_template("partners.html")

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    if request.method == 'POST':
        add_new_user(request.form['username'], request.form['password'])
        return redirect("http://" + address + ":5000/login", code=302)
    return render_template('create_account.html')

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

if __name__ == '__main__':
    app.run()