from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
import json

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template("airline1/index.html")

if __name__ == '__main__':
    app.run()