from flask import Flask, render_template, redirect, url_for, request, flash
import json

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template("airline1/index.html")

if __name__ == '__main__':
    app.run()