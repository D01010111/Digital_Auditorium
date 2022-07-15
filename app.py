from audioop import add
import requests
import config, ccxt, time
from flask import Flask, render_template, request, flash, redirect, url_for
from web3 import Web3

app = Flask(__name__, template_folder="templates")
w3 = Web3(Web3.HTTPProvider(config.Node_url))

def get_eth_price():
    binance = ccxt.binance()
    eth_price = binance.fetch_ticker('ETH/USDC')
    return eth_price

def get_btc_price():
    binance = ccxt.binance()
    btc_price = binance.fetch_ticker('BTC/USDC')
    return btc_price

    

@app.route('/')
def index():
    eth = w3.eth

    binance = ccxt.binance()
    eth_price = get_eth_price()
    btc_price = get_btc_price()

    latest_blocks = []
    for block_number in range(eth.block_number, eth.block_number-10, -1): #go ten blocks back increments of 1
        block = eth.get_block(block_number)
        latest_blocks.append(block)

    latest_transactions = []
    for tx in latest_blocks[-1]['transactions'][-10:]:
        transaction = eth.get_transaction(tx)
        latest_transactions.append(transaction)

    current_time = time.time()


    return render_template(
        'index.html',
        miners=config.miners,
        current_time=current_time,
        eth=eth, 
        eth_price=eth_price, 
        btc_price=btc_price,
        latest_blocks=latest_blocks,
        latest_transactions=latest_transactions
        )

@app.route('/transaction/<hash>')
def transaction(hash):
    tx = w3.eth.get_transaction(hash)
    value = w3.fromWei(tx.value, 'ether')
    receipt = w3.eth.get_transaction_receipt(hash)
    eth_price = get_eth_price()

    gas_price = w3.fromWei(tx.gasPrice, 'ether')

    return render_template('transaction.html', tx=tx, value=value, receipt=receipt, gas_price=gas_price, eth_price=eth_price)

@app.route('/address')
def address():
    address = request.args.get('address')
    eth_price = get_eth_price()

    try:
        address = w3.toChecksumAddress(address)
    except:
        flash('Address is not valid')
        return redirect('/')

    balance = w3.eth.get_balance(address)
    balance = w3.fromWei(balance, 'ether')

    return render_template('address.html', eth_price=eth_price, address=address, balance=balance)

@app.route('/block/<block_number>')
def block(block_number):
    block = w3.eth.get_block(int(block_number))
    return render_template('block.html', block=block)


app.run()