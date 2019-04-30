from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from bson.json_util import dumps
import uuid
from flask_restful import Resource, Api
from requests import put, get
from web3 import Web3, HTTPProvider, contract
import json
import os.path
import time

loginList = list()
loginMap = dict()
address = '127.0.0.1'

# Contract setup
contract_address = "0x089cB3A8C19C5b20cABAdF0691dAD52083FD7Aa2"
airline1_wallet_addr = "0xE75D9DE667F7FFaCD7a300E02dc4e6654598cA77"
airline2_wallet_addr = "0x75727A4010ae3dcB81aF56e7aCcCFa1Ee4AB08a3"
airline1_private_key = "2CE8FABF78D208C16CC4C9A6A379AD83BD8AFAEB52B82CA918B4670D71B9EF42"
airline2_private_key = "197D0CA5903BD0DAF21076F09D1A6AC2D780D3010E531B5CFBB7CD7A69E275F1"
infura_url = "https://ropsten.infura.io/v3/c5aa7254666449beb6f5a5d8536313dd"

with open(os.path.dirname(__file__) + '/../../smart_contract/abi.json') as f:
    info_json = json.load(f)
abi = info_json

w3 = Web3(HTTPProvider(infura_url))
w3.eth.enable_unaudited_features()
contract = w3.eth.contract(address = contract_address, abi = abi)
app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://lab2:ssHIbMqjtPAEGCLf@cluster0-moytw.mongodb.net/airline1?retryWrites=true'
mongo = PyMongo(app)
api = Api(app)

class Response(Resource):
    def get(self):
        customerName = get('http://127.0.0.1:5000/request').json()
        responseResult = validateCustomerReservation(customerName) # 1 if we can accept customer
        return {'result': responseResult}

class Request(Resource):
    def get(self):
        username = loginMap[request.remote_addr]
        return {'result': username}

api.add_resource(Response, '/response')
api.add_resource(Request, '/request')

#TODO:
# Verify this airline can take a given customer. return 1 if yes, 0 no.
def validateCustomerReservation(customerName):
    # Look through database to determine output
    return 1

# BLOCKCHAIN FUNCTIONS #########################################################################
def proccess_transaction_blockchain(txn_dict):
    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=airline2_private_key)
    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.getTransactionReceipt(result)
    count = 0
    while tx_receipt is None and (count < 30):
        time.sleep(5)
        tx_receipt = w3.eth.getTransactionReceipt(result)
        count += 5
        print(tx_receipt)

    if tx_receipt is None:
        print("Transaction failed!")
        return False
    return True

def request_blockchain(toAirline, details):
    nonce = w3.eth.getTransactionCount(airline2_wallet_addr)
    txn_dict = contract.functions.request(w3.toChecksumAddress(toAirline), str(details)).buildTransaction({
        'chainId': 3,
        'gas': 1400000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })
    proccess_transaction_blockchain(txn_dict)


def response_blockchain(fromAirline, details, successful):
    nonce = w3.eth.getTransactionCount(airline2_wallet_addr)
    txn_dict = contract.functions.response(w3.toChecksumAddress(fromAirline), str(details), (successful['result'] == 1)).buildTransaction({
        'chainId': 3,
        'gas': 1400000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })
    proccess_transaction_blockchain(txn_dict)
#@app.route('/performTransfer')
#def transfer_customer():

####################################################################################################################

# add_new_user
# @username(string): user's ID(e.g. jsmith)
# @password(string): password
# @name(string): user's name(e.g. John Smith)
# Purpose: adds a user to the database
def add_new_user(username, password, name):
    if mongo.db.customers.find_one({"userID": username}):
        return False
    else:
        mongo.db.customers.insert_one({"customerName": name, "userID": username, "password": password})
        return True
    return False

# valid_user
# @username(string): user's ID(e.g. jsmith)
# @password(string): password
# Purpose: Checks whether a user exists in the database or not using username
def valid_user(username,password):
    if mongo.db.customers.find_one({"userID": username}):
        if mongo.db.customers.find_one({"userID": username})['password'] == password:
            return True
    return False


# createReservation
# fromLoc(string): Departing location
# toLoc(string): Destination
# date(string): Date(e.g. 12/31/2019)
# userID(string): User ID
# Purpose: adds a reservation to the database
def createReservation(fromLoc,toLoc,date,userID):
    tempRevID = str(uuid.uuid4())
    while mongo.db.reservations.find_one({"revID": tempRevID}):
        tempRevID = str(uuid.uuid4())
    mongo.db.reservations.insert_one({"from": fromLoc, "to": toLoc, "date": date,"customer":userID, "revID":tempRevID})

# getReservations
# username(string): userID
# Purpose: Gets all reservations for a specific customer
def getReservations(username):
    listToReturn = []
    for reserv in mongo.db.reservations.find({"customer": username}):
        listToReturn.append(reserv)
    print(listToReturn)
    return listToReturn

# deleteOneReservation
# revID(string): Reservation ID
# Purpose: Deletes a reservation from the database
def deleteOneReservation(revID):
    if mongo.db.reservations.delete_one({"revID": revID}):
        return True
    return False

# getOneReservation
# revID(string): Reservation ID
# Purpose: Get a reservation from the database
def getOneReservation(revID):
    return mongo.db.reservations.find_one({"revID": revID})




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
        return redirect("http://" + address + ":5001/login", code=302)

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
            return redirect("http://" + address + ":5001/reservation.html", code=302)
    else:
        return redirect("http://" + address + ":5001/login", code=302)
    return render_template('book.html', error=error)


@app.route('/partners.html')
def partners():
    return render_template("partners.html")

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    if request.method == 'POST':
        add_new_user(request.form['username'], request.form['password'],request.form['name'])
        return redirect("http://" + address + ":5001/login", code=302)
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
        return redirect("http://" + address + ":5001/", code=302)
    return render_template('login.html', error=error)

@app.route('/getUserName')
def getUserName():
    return ""

@app.route('/changeAirline', methods=['GET', 'POST'])
def changeAirline():
    details = loginMap[request.remote_addr] + " requests a change to airline " + airline1_wallet_addr
    print(details)
    # Put request on blockchain
    request_blockchain(airline2_wallet_addr, details)
    # Once finished, we call the response function on the OTHER AIRLINE.
    result = get('http://127.0.0.1:5000/response').json()
    print(result)
    # If it returns 1 (they can take the customer) then update DB
    #TODO:
    #if(result == 1):
        # Update DB shit

    # Call response function in smart contract to put transaction on blockchain
    response_blockchain(airline2_wallet_addr, details, result)
    return render_template('index.html')

@app.route('/returnReservations', methods=['GET', 'POST'])
def returnReservations():
    reservationsToReturn = getReservations(loginMap[request.remote_addr])
    return dumps(reservationsToReturn)

if __name__ == '__main__':
    app.run()