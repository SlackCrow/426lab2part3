from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
import json

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://lab2:ssHIbMqjtPAEGCLf@cluster0-moytw.mongodb.net/test?retryWrites=true'
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/index.html')
def index():
    return render_template("index.html")

@app.route('/reservation.html')
def reservation():
    return render_template("reservation.html")

@app.route('/partners.html')
def partners():
    return render_template("partners.html")

if __name__ == '__main__':
    app.run()