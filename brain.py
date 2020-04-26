import csv
import numpy as np
import matplotlib.pyplot as plt

TRADING_FEE = 0.002
PRICE_PRECISION = 4
AMOUNT_PRECISION = 8

def round_off(x, num_sig_dig = 16):
    # FIXHERE0: problem with np.mean
    # return round(x - 0.5*10**num_sig_dig, num_sig_dig) 
    tmp_str = str(x)
    tmp_lst = tmp_str.split(".")
    tmp_lst[1] = tmp_lst[1][:num_sig_dig]

    return float(".".join(tmp_lst)) 

#-------------------- 

# FIX: round_off stuff
FEE_LOSS_SQ = (1-TRADING_FEE)**2 

#-------------------- 

def cal_profit_rate(enter_amount = 1, enter_rate = 1, target_profit = 0):
    return round_off((target_profit/enter_amount + 1)*enter_rate/FEE_LOSS_SQ, PRICE_PRECISION)


if __name__ == "__main__":
    # ISSUE, the amount is in PZM
    
    total_profit = 0
    enter_amount = 10
    target_profit = 0.1 
    max_thread = 4
    max_price = 1000

    file_path = "data/PZM_USD 2020-04-26 19:22:46.csv"

    data = []

    open_order = []
    error_order = []
    success_order = []

    with open(file_path, 'r') as f:
        data = f.readlines()
    
    for row in data[:110]:
        r = row.split(',')

        timestamp = r[0]
        bid = float(r[1])
        ask = float(r[2])
        hist_data = [float(p) for p in r[3:]]

        # 1. avg price
        avg_price = round_off(np.mean(hist_data))

        # 2. last price
        last_price = hist_data[-1]

        # STEP 1: Buy low 
        
        ## buy threshold 
        try:
            max_price = max([od["enter_price"] for od in open_order])
        except:
            pass

        buy_threshold = min(avg_price, max_price)

        if buy_threshold > ask:
            bid_price = ask

            exit_price = cal_profit_rate(enter_amount, bid_price, target_profit)

            order_amount = round_off(enter_amount/bid_price, AMOUNT_PRECISION)
            
            # stage 0: preparing order data
            my_order = {"stage" : 0,
                        "type" : "buy", 
                        "amount" : order_amount, 
                        "enter_price" : bid_price, 
                        "exit_price" : exit_price }

            if len(open_order) < max_thread:
                try:
                    # stage 1: creating buy order
                    # GOHERE0: API call to place a buy order

                    my_order["stage"] = 1
                    open_order.append(my_order)
                    pass
                except:
                    error_order.append(my_order)
                    print("ERROR: unable to place a buy order")

                try: 
                    # stage 2: checking if the buy order is filled
                    # GOHERE1: API call to check the bid order status

                    if True:
                        my_order["stage"] = 2 # if the buy order is filled update the stage
                except:
                    print("ERROR: unable to check bid order status")
    
                if my_order["stage"] > 0:
                    open_order.append(my_order)
        
        ## STEP 2: check the order status 
        for i, order in reversed(list(enumerate(open_order))):
            # GOHERE4: API call to update status of all the open_order 
            pass

            # GOHERE5: check on stage 1 orders
            if order["stage"] == 1:
                # GOHERE6: IF the order is filled moved up the stage

                if True: 
                    my_order["stage"] = 2

            # Checking for selling condition
            if (my_order["stage"] == 2) and (order["exit_price"] <= bid):

                sell_rate = bid

                try:
                    # stage 3: creating sell order
                    # GOHERE2: API call to place a sell order with the target price
    
                    my_order["stage"] = 3
                    pass
                except:
                    print("ERROR: unable to place a sell order")

            if my_order["stage"] == 3:
                # stage 4: everything complete - make some profit
                try:
                    # GOHERE: API call to check on the status of the sell order
                    pass
                    
                    if True:
                        my_order["stage"] = 4
                except:
                    print("ERROR: unable to track a sell order")

            # GOHERE7: transfer success order to complete
            if order["stage"] == 4: 
                howdy = open_order.pop(i)
                howdy["stage"] = 4
                success_order.append(howdy)
                profit = round_off(howdy["amount"] * howdy["exit_price"]*(1-0.002), AMOUNT_PRECISION) - enter_amount
                print("Order exited! Profit: ", profit)
                total_profit+=profit


    print("Num exited order: ", len(success_order), "Total profit: ", total_profit)
