en = enter amount
ex = exit amount
c = crypto bought
f = transaction fee

r_b = bid rate, use for enter, price I pay for to get cypto
r_a = ask rate, use for exit, price I use to selling cypto

p = profit

- - - - - - - - - - 

c = en*1/r_b*(1-f)

ex= c*r_a*(1-f)

p = en*r_a/r_b*(1-f)^2 - en = en(r_a/r_b*(1-f)^2 - 1)

r_a = (p+en)*r_b/(en*(1-f)^2) = en*(p/en +1 )*r_b/(en*(1-f)^2) = (p/en + 1)*r_b/(1-f)^2

p/en = r_a/r_b*(1-f)^2 - 1
p/en + 1 = r_a/r_b*(1-f)^2 
r_a = (p/en +1)*r_b/(1-f)^2


# Trategy A

Every hours update the price distribution

Enter:
    - bid price is lower than the average
    - target profit rate is lower than the max price
    - bid price is lower than the most recent exit rate

Exit:
    - exit when the current rate is higher than the target profit rate

During that hour:
    - check bid and ask price
    - buy if the price is at the lower quantile
    - sell if the price is at upper quantile
    - Check on trade cycles 

Trade cycle:
    - BEGIN: buy lower quantile
    - LIVING: check on bid_ask rate every minutes
    - END: sell when profit is greater or equal to 0.1

Time weighted distribution:
    - Count the past less 
    - Count the present 
    - time-distant weighted average price

Ressistance:
    - find the resistance level
    - get the lowest of the peaks

Simulation of data to estimate profit 


--- 

When place a buy order the amount is in BTC

When place sell order the amount is in BTC
