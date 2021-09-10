import json, config, requests, traceback
from datetime import datetime
from flask import Flask, request
from binance.client import Client
from binance.enums import *
from binance.exceptions import *


# Send an error report to the specified Discord Group
def send_report(report):
    if config.REPORT:
        message = "@everyone " + report
        requests.post(config.DISCORD_ERROR_LINK,
                      data={"content": message},
                      headers=config.DISCORD_HEADER)

app = Flask(__name__)

# Binance Client
client = Client(config.API_KEY, config.API_SECRET, testnet=False)


# Index page
@app.route('/')
def hello_world():
    return 'Hello, World!'


# Address for receiving pings to avoid idling
@app.route('/ping', methods=['POST'])
def ping():
    return "Pinged!"


# Address for receiving webhooks
@app.route('/webhook', methods=['POST'])
def webhook():
    try:

        # Change JSON object from webhook to a python dictionary
        data = json.loads(request.data)

        # Check if safety key is matching
        if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
            send_report("Incorrect Passcode!")
            return {
                "code": "error",
                "message": "Access Denied!"
            }

        side = data['strategy']['order_action'].upper()
        action = data['strategy']['order_comment'].upper()
        quantity = config.QUANTITY

        try:
            client.futures_create_order(symbol="ETHBUSD", side=side, type='MARKET', quantity=quantity)
        except BinanceAPIException as e:
            print(e)
            send_report(str(e.message) + "During Entry")
            return {
                "code": "error",
                "message": "Binance Error!"
            }

        if action != "CLOSE":

            try:
                client.futures_create_order(symbol="ETHBUSD", side=side, type='MARKET', quantity=quantity)
            except BinanceAPIException as e:
                print(e)
                send_report(str(e.message) + "During Entry")
                return {
                    "code": "error",
                    "message": "Binance Error!"
                }

    except BinanceAPIException as e:
        print(e)
        send_report(str(e.message))