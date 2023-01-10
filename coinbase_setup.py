import hmac
import hashlib
import time 
import requests
import pandas as pd
import sqlite3
import datetime
import os 
from not_secrets import coinbase_key,coinbase_secret
from update_crypto_db import product_list_2,base_currency,coinbase_interval

#creation of db folder if it does not exist
dir= "E:\Crypto_DB\Coinbase_DB"
if not os.path.exists(dir):
    os.makedirs(dir)

def get_coinbase_pairs():

    coinbase_pairs = {}
    timestamp = str(int(time.time()))
    method= "GET"
    url_path=  "/api/v3/brokerage/products"
    url = "https://api.coinbase.com/api/v3/brokerage/products?&product_type=SPOT"

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
    response=response.json()

    products= pd.DataFrame(response['products'])

    for x in product_list_2:
        for y in base_currency: 
            coinbase_ticker= str(x+"-"+y)
            for match in products.product_id: 
                if coinbase_ticker == str(match):
                    coinbase_pairs[match]= 1
    return coinbase_pairs

def get_last_date(table_name):
    dir= "E:\Crypto_DB\Coinbase_DB"
    db_file= os.path.join(dir,"coinbase.db")
    conn= sqlite3.connect(db_file)
    c= conn.cursor()

      # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = c.fetchall()
    if table_name not in [table[0] for table in table_names]:
        return None

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

   # Check if the last date is at least 6 hours ago
    if current_time - last_date >= interval:
        return last_date
    else:
        return "Not yet"


def run_coinbase_DB():
    dir= "E:\Crypto_DB\Coinbase_DB"
    db_file= os.path.join(dir,"coinbase.db")
    conn= sqlite3.connect(db_file)
    symbol_list = get_coinbase_pairs()
    time.sleep(4.0)
    for pair in symbol_list:
       
        time.sleep(1)
        df_list=[]
        
        
        table_name= pair.replace("-","_") 

        #checks if the table even exist if so grabs last date and makes our date range for calling


        if get_last_date(table_name) == None: 
            
                start_date = "2019-01-03"
                end_date = "2022-05-03"

                # Convert UTC time to Unix time (seconds since Jan 1, 1970)
                date_range = pd.date_range(start_date, end_date,freq="MS")
                
                # Convert UTC time to Unix time (seconds since Jan 1, 1970)
                date_index = pd.date_range(start_date, end_date,freq="25D")

                #df list to concat at the end
                df_list= []
                #go through date range now for api calls
                for date in date_index:
                    print(str(pair)+ " "+ str(date)) 

                    #get rid of the decimal when changing to unix
                    first_date= round((time.mktime(date.timetuple())))
                    

                        #api limits 300 candles /request fyi 
                    second_time= date+pd.offsets.Day(25)
                    second_date= round((time.mktime(second_time.timetuple())))


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
                    time.sleep(1.2)
                    #check if we got response 200
                    if str(response)== "<Response [200]>":
                    

                    # if we do lets put the data in our dataframe list
                        response = response.json()
                        first_df= pd.DataFrame(response['candles'])
                        df_list.append(first_df)
                    
                
                
                #if we dont lets skip to the next date range. remember we still need to follow the api rate limit even if we do not get anything. 
                    else:
                        print(response) 
                        continue
            
        #now put together your df list and put it into the sql database for storage
        second_df=pd.concat(df_list)

        #converts to UTC TIME
        pair= pair.replace("-","_") 
        second_df['start']= pd.to_datetime(second_df['start'], unit='s',origin= 'unix')
        second_df.to_sql(str(table_name),
                        conn, 
                        if_exists="append",
                        index=False)
            #if we dont lets skip to the next date range. remember we still need to follow the api rate limit even if we do not get anything. 
    
                    
        #now put together your df list and put it into the sql database for storage
            
print(run_coinbase_DB())
