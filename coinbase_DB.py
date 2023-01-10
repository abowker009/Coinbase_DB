import hmac
import hashlib
import time 
import requests
import pandas as pd
import sqlite3
import datetime
import os 
from not_secrets import coinbase_key,coinbase_secret
from update_crypto_db import coinbase_interval

dir= "E:\Crypto_DB\Coinbase_DB"

def get_coinbase_pairs():
    # Connect to the database
    db_file= os.path.join(dir,"coinbase.db")
    conn= sqlite3.connect(db_file)
    c = conn.cursor()

    # Get the list of table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    official_coinbase_pairs = [table[0] for table in c.fetchall()]

    # Close the connection
    conn.close()

    return official_coinbase_pairs

def get_last_date(table_name):
    dir= "E:\Crypto_DB\Coinbase_DB"
    db_file= os.path.join(dir,"coinbase.db")
    conn= sqlite3.connect(db_file)
    c= conn.cursor()
    
    # Query last date in table
    query = 'SELECT MAX(start) FROM {}'.format(table_name)
    c.execute(query)
    last_date = c.fetchone()[0]

    # Close connection to database
    c.close()
    conn.close()

    last_date= pd.to_datetime(last_date)

    #get the current time in utc
    current_time= datetime.datetime.utcnow()

    #create the invterval so it can tell if it has an 5 hour time to get
    interval = datetime.timedelta(hours=5)

   # Check if the last date is at least 5 hours ago
    if current_time - last_date >= interval:
        return last_date
    else:
        return "Not yet"

def run_coinbase_DB():
    dir= "E:\Crypto_DB\Coinbase_DB"
    db_file= os.path.join(dir,"coinbase.db")
    conn= sqlite3.connect(db_file)
    symbol_list = get_coinbase_pairs()

# set the end date here so all pairs end at the exact same time. Helps with db organization FYI 
    current_time = datetime.datetime.utcnow()
    interval = datetime.timedelta(hours=5)

    # Subtract the interval from the current time to get 5 hours behind
    time_minus_5_hours = current_time - interval
    time_string = time_minus_5_hours.strftime("%Y-%m-%d %H:%M:%S")
    end_date= datetime.datetime.strptime(time_string,"%Y-%m-%d %H:%M:%S")
    end_date= end_date.replace(second=0)

    for table_name in symbol_list: 


        # format table name corectly for coinbase API
        pair= table_name.replace("_","-")


#CREATION OF DATE RANGE 
        if str(get_last_date(table_name)) == "Not yet":
            continue

        else: 
            #First get the last date from the sql db
            first_date= (get_last_date(table_name))

            #now date range for every 300 minutes 
            date_index= pd.date_range(first_date,end_date,freq="300T")
            
            for date in date_index:

                #shows progress of what date is being taken 
                print(str(pair)+ " "+ str(date))


                #get rid of the decimal when changing to unix
                first_date= round((time.mktime(date.timetuple())))
                #api limits 300 candles /request fyi 
                second_time= date+pd.Timedelta("300 minute")
                second_date= round((time.mktime(second_time.timetuple())))
                
                
                #CREATION OF AUTH 
                timestamp = str(int(time.time()))
                method= "GET"
                url_path=  "/api/v3/brokerage/products/"+str(pair)+"/candles"
                url = "https://coinbase.com/api/v3/brokerage/products/"+str(pair)+"/candles?start="+str(first_date)+"&end="+str(second_date)+"&granularity="+str(coinbase_interval)
                body=""

                message = timestamp+ method+ url_path+ body
                signature = hmac.new(coinbase_secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()


                headers = {
                    "accept": "application/json",
                    "CB-ACCESS-KEY": coinbase_key,
                    "CB-ACCESS-SIGN": signature.hex(),
                    "CB-ACCESS-TIMESTAMP": timestamp
                }

                response = requests.get(url, headers=headers)
                
                time.sleep(.15)

                #checks what kind of response we get 
                if str(response) != "<Response [200]>":
                    print(response)
                    continue  # Move on to the next iteration of the loop

                # if we do lets put the data in our dataframe list
                response = response.json()
                

                first_df= pd.DataFrame(response['candles'], columns=["start","low","high","open","close","volume"])
                first_df['start']= pd.to_datetime(first_df['start'], unit='s',origin= 'unix')
                first_df.to_sql(str(table_name),
                        conn, 
                        if_exists="append",
                        index=False)


print(run_coinbase_DB())
