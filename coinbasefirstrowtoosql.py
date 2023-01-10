import pandas as pd 
import os 
import sqlite3


dir= "E:\Crypto_DB\Coinbase_DB"
db_file= os.path.join(dir,"coinbase.db")
for root, dirs, files in os.walk("Coinbase_ohlc"):
    for file in files:
        symbol= file.replace(".csv","") 
        print(symbol)
        df= pd.read_csv(os.path.join(root,file),header=0)
        conn= sqlite3.connect(db_file)
        symbol= symbol.replace("_","-")
        df.to_sql(str(symbol),
                                conn, 
                                if_exists="append",
                                index=False)
