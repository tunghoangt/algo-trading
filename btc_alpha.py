import requests
import functools

import json
import hmac
import hashlib

from time import time
from time import sleep

from urllib.parse import urlencode

def round_off(x, num_sig_dig):
    # FIXHERE0: problem with np.mean
    # return round(x - 0.5*10**num_sig_dig, num_sig_dig) 
    tmp_str = str(x)
    tmp_lst = tmp_str.split(".")
    tmp_lst[1] = tmp_lst[1][:num_sig_dig]

    return float(".".join(tmp_lst)) 

live_api = "https://btc-alpha.com/api/"

CURRENCIES_ENDPOINT = "v1/currencies/" # GET
PAIRS_ENDPOINT = "v1/pairs/" # GET
WALLETS_ENDPOINT = "v1/wallets/" # GET
ORDER_ENDPOINT = "v1/order/" # POST or GET
ORDER_OWN_ENDPOINT = "v1/orders/own" # POST or GET
ORDER_CANCEL_ENDPOINT = "v1/order-cancel/" # POST
EXCHANGE_ENDPOINT = "v1/exchanges/" # GET
OWN_EXCHANGE_ENDPOINT = "v1/exchanges/own" # GET
ORDERBOOK_ENDPOINT = "v1/orderbook/" # GET


LIST_PAIRS = {
    "endpoint_url": PAIRS_ENDPOINT,
    "method" : "get"
}

WITHDRAWAL_BALANCES = {
    "endpoint_url":WALLETS_ENDPOINT,
    "method":"get"
}

TRADING_TRADE = {
    "endpoint_url":ORDER_ENDPOINT,
    "method":"post"
}

TRADING_CANCEL = {
    "endpoint_url":ORDER_CANCEL_ENDPOINT,
    "method":"post"
}

TRADING_ORDER = {
    "endpoint_url":ORDER_ENDPOINT,
    "method":"get"
}

TRADING_OWN_ORDER = {
    "endpoint_url":ORDER_OWN_ENDPOINT,
    "method":"get"
}

MARKET_TICKER = {
    "endpoint_url":ORDERBOOK_ENDPOINT,
    "method":"get"
}

EXCHANGE = {
    "endpoint_url":EXCHANGE_ENDPOINT,
    "method":"get"
}

VOCABILARY_ORDER_STATUS = {
    1:"active", # order in queue for executing
    2:"canceled", # order not active, permanently 
    3:"done", # order fully executed
    "active":1,
    "canceled":2,
    "done" : 3
}

def flatten_lst(l):
    return [item for sublist in l for item in sublist]


class BtcAlphaClient:
    def __init__(self, api_key = None, api_secret = None, exchange_rate = 0.002):
        self.path = live_api
        
        # Authorization
        self.api_key = api_key
        self.api_secret = api_secret
        self.auth_headers = {}
        
        self.exchange_rate = exchange_rate 
        self.trading_pairs = self.request(LIST_PAIRS)


    def get_auth_headers(self, data = {}):
        """
                Generate autorization header | needed for authorization
        """
        msg = self.api_key + urlencode(sorted(data.items(), key=lambda val: val[0]))
        
        sign = hmac.new(self.api_secret.encode(), msg.encode(), digestmod='sha256').hexdigest()
        
        return {
            'X-KEY': self.api_key,
            'X-SIGN': sign,
            'X-NONCE': str(int(time() * 1000)),
        }

    def request(self, endpoint_data, params = {}, auth = False):
        method = endpoint_data['method']
        request_url = self.path + endpoint_data['endpoint_url']

        if auth:
            auth_headers = self.get_auth_headers(params)
        else:
            auth_headers = {}

        if (method == "post"):
            response = requests.post(request_url, data = params, headers = auth_headers)
        if (method == "get"):
            response = requests.get(request_url, params = params, headers = auth_headers)
        
        print(auth_headers)
        response.raise_for_status() # notify HTTP error

        response = response.json()

        return response
    
    def getBalances(self):
        # work on formating
        response = self.request(WITHDRAWAL_BALANCES, auth=True);
        return response

    def getBalance(self, curr):
        # work on formating
        response = self.request(WITHDRAWAL_BALANCES, auth=True);
        for res in response:
            if res['currency'] == curr:
                return float(res['balance'])
        return None
    
    def getTicker(self, trading_pair):
        # GOHERE0
        market_ticker = MARKET_TICKER.copy()
        market_ticker['endpoint_url'] += trading_pair
        
        orderbook = self.request(market_ticker)
        
        try:
            max_bid = orderbook["buy"][0] 
        except IndexError:
            max_bid = {"price" : 0, "amount" : 0}

        try:
            min_ask = orderbook["sell"][0]
        except IndexError:
            min_ask = {"price" : 0, "amount" : 0}
        spread = min_ask["price"] -  max_bid["price"]
        res = {"trading_pair" : trading_pair,
               "bid" : max_bid["price"], "ask" : min_ask["price"], 
               "spread" : spread,
               "max_ask_vol" : min_ask["amount"], "max_bid_vol" : max_bid["amount"]}
        return res

    def processOrder(self,raw_order):
        raw_order["status"] = VOCABILARY_ORDER_STATUS[raw_order["status"]]
        raw_order["amount"] = float(raw_order["amount"])
        raw_order["price"] = float(raw_order["price"])

        return raw_order

    def getOrder(self, orderId):
        # GOHERE1
        trading_order_tmp = TRADING_ORDER.copy()
        trading_order_tmp['endpoint_url'] += str(orderId)
        response = self.request(trading_order_tmp)
        raw_order = response

        return self.processOrder(raw_order)

    def listPairs(self, cur1, cur2):
        params = {'currency1':cur1, 'currency2':cur2}
        response = self.request(LIST_PAIRS, params=params)
        raw_order = response

        return raw_order

    def getOwnOrder(self):
        # Done
        response = self.request(TRADING_OWN_ORDER, auth=True)
        raw_order = response
        
        return raw_order

    def placeOrder(self, trading_pair, side=None, size=None, price=None):
        # GOHERE2

        #price = float(price)
        #size = float(size)

        params = {
                "type" : side, # type of order "sell" or "buy"
                "pair" : trading_pair, # pair of order
                "amount" : size, # Amount of first currency pair
                "price" : price # price of order 
        }

        print(params)
        try:
            raw_response = self.request(TRADING_TRADE,params=params,auth=True)

            return raw_response
        except Exception as e:
            return {"error" : str(e)}
        
    def cancelOrder(self,orderId):
        """
        NEED some fix
        """
        params = {
            "order": orderId
        }
        
        try:
            response = self.request(TRADING_CANCEL,params=params,auth=True)
            
            if str(response["order"]) == orderId:
                return True
            else:
                return False
        except Exception as e:
            return {"error" : str(e)}
            return False

    def getExchanges(self, pair = "BTC_USD", depth = 1, delta = 100):
        # GOHERE EXCHANGE
        offset = 0
        exchange_lst = []
        count = 0

        while(count < depth):
            params = {
                "pair" : pair, 
                "limit" : delta,
                "offset" : offset,
                }
    
            try:
                raw_response = self.request(EXCHANGE, params=params, auth=False)
            except Exception as e:
                return {"error" : srt(e)}

            exchange_lst.append(raw_response)
            offset+=delta 
            count+=1
    
        exchange_lst = flatten_lst(exchange_lst) # flatten if there are multiple offsets
        return exchange_lst 

    def getExchangeData(self, pair = "BTC_USD", depth = 1):
        
        # MODIFY: global data holder, get and update functions, avoid multiple overlapping queries
    
        exchange_lst = self.getExchanges(pair, depth)
        timestamp_lst = [e["timestamp"] for e in exchange_lst]
        price_lst = [float(e["price"]) for e in exchange_lst]
    
        return [timestamp_lst, price_lst]

if __name__ == "__main__":
    
    pair = "PZM_USD"

    api_key = ''
    api_secret = ''

    btcAlpha = BtcAlphaClient(api_key = api_key, api_secret = api_secret)

    #balance = btcAlpha.placeOrder(trading_pair = "PIRL_BTC", side = 'buy', size = 40, price = 0.00000250)

    #balance = btcAlpha.getBalance("BTC")

    #tmp = btcAlpha.getTicker(pair)
    p = 0.0551 
    enter_amount = 7
    
    # ROUND OFF WORK
    o_s = round_off(enter_amount/p, 8)
    s_s = round_off(enter_amount/p, 7)

    print(o_s)
    tmp = btcAlpha.placeOrder(trading_pair = "PZM_USD", side = "buy", size = o_s, price = p)
    #tmp = btcAlpha.placeOrder(trading_pair = "PZM_USD", side = "sell", size = s_s, price = p)

    #tmp = btcAlpha.getOrder("186824699")
    #tmp = btcAlpha.cancelOrder("186824074")
    

    #tmp = btcAlpha.getExchangeData(depth=3)


    print(tmp)
