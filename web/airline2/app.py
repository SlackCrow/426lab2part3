from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from web3 import Web3, HTTPProvider, contract
import json
import os.path
import time

# Contract setup
contract_address = "0x089cB3A8C19C5b20cABAdF0691dAD52083FD7Aa2"
airline1_wallet_addr = "0xE75D9DE667F7FFaCD7a300E02dc4e6654598cA77"
airline2_wallet_addr = "0x75727A4010ae3dcB81aF56e7aCcCFa1Ee4AB08a3"
airline1_private_key = "2CE8FABF78D208C16CC4C9A6A379AD83BD8AFAEB52B82CA918B4670D71B9EF42"
airline2_private_key = "197D0CA5903BD0DAF21076F09D1A6AC2D780D3010E531B5CFBB7CD7A69E275F1"
infura_url = "ropsten.infura.io/v3/c5aa7254666449beb6f5a5d8536313dd"

with open(os.path.dirname(__file__) + '/../../smart_contract/abi.json') as f:
    info_json = json.load(f)
abi = info_json

w3 = Web3(HTTPProvider(infura_url))
w3.eth.enable_unaudited_features()
contract = w3.eth.contract(address = contract_address, abi = abi)
app = Flask(__name__)

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
    txn_dict = contract.functions.request(int(toAirline), str(details)).buildTransaction({
        'chainId': 3,
        'gas': 1400000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })
    proccess_transaction_blockchain(txn_dict)

def response_blockchain(fromAirline, details, successful):
    nonce = w3.eth.getTransactionCount(airline2_wallet_addr)
    txn_dict = contract.functions.response(int(fromAirline), str(details), bool(successful)).buildTransaction({
        'chainId': 3,
        'gas': 1400000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })
    proccess_transaction_blockchain(txn_dict)

@app.route('/')
def hello():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)