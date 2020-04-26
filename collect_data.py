from btc_alpha import BtcAlphaClient
import time
import datetime

def get_timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":

    pair = "PZM_USD"
    delay = 5*60 # delay for 5 minutes
    file_path = "data/" + pair + " " + get_timestamp() + ".csv"

    btcAlpha = BtcAlphaClient()

    count = 0
    while True:
        count+=1
        timestamp = get_timestamp()

        ticker = btcAlpha.getTicker(pair)

        bid = ticker["bid"]
        ask = ticker["ask"]

        exchange_data = btcAlpha.getExchangeData(pair, depth=3)
        price_data = exchange_data[1]
        #print(len(price_data))
        row = [timestamp, bid, ask] + price_data
        
        row = [str(i) for i in row]
        with open(file_path, 'a') as f:
            f.write(','.join(row))
            f.write('\n')

        print(timestamp, " - ", count)
        time.sleep(delay)
