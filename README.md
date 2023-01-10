# Coinbase_DB
This will create a SQL Database for OHLC data from the Advance Trade Coinbase API. update_crypto_db.py and not_secrets.py will also be use for other databases for example Binance.US. I have set it so your database will not update prices if it has been 5 hours or less since the last update just for Coinbase. Note if you are already using Advance Trade Coinbase API you may run into API rate limits so please take note of this before starting. Below I will list the order of the files you need to run to get everything set up. Please message me for any problems you run into. 

IMPORTANT: in each file dir="" I have a seperate drive for my DB which is in drive "E" you will need to change this to the directory you will want everything stored in so change for you own use.

1. You need to create an API key from Coinbase. Before creation make sure your API version is updated to the most current one (FYI make    sure you are on Chrome for creation as Safari will not work) . For example I used a pair I will never trade and these are the permissions I allowed wallet: accounts: read; wallet: notifications: read; wallet: user:read. After creation put both the key and secret in its respective place in not_secrets.py.

2. Open update_crypto_db.py: 
Go to product list and put your product that you would like to get data for. For the first time as an example and see if everything     works make product_list = ["BTC","ETH] and base_currency= ["USD"] (make sure to capitalize every letter) Dont worry if every pair has all of the base_currency in them as the program will figure this out itself.
 
3. Open coinbase_setup.py: 
Now we need to set up the Database and grab the first dates of your tickers. Currently there is not an easy way of grabbing the first dates of each pair so I decided to grab the third day of every month starting in 2019. You can change the start dates and end dates in coinbase_setup.py if you want but since markets have changed dramatically since 2020 I decided dates before 2019 would not be helpfull. DO NOT STOP IT BEFORE ITS DONE. 

4. Open coinbase_firstohlc.py: 
Now that we have the "somewhat" first dates of each pair we need to delete all of the other data we got from the API. Just run this file as it is just a script. 

5. Open coinbasefirstrowtoosql.py: 
Before we start make sure your csv files are in the same directory (folder) before beginning. If they are, take note of where you want to store your DB (dir = "") and then run this file. If everything works smoothly congrats! You know how the beggining dates of you of your tickers and can finally run the main file to get everything updated. 

6. Before you begin this step if you are running your first trial run and made sure everything runs you can go ahead and delete EVERYTHING (VERY IMPORTANT). Now go back to step #2 and change your product_list and base_currency to the pairs you want and go through each of the steps again. Once you have head to #7. 

7. Congrats you are ready to have the data you want but here are some important points you need to take note of. I currently have it setup so it pulls minute OHLCV data. If you would like to pull hourly you will need to change the interval in update_crypto.py and also the interval in the #CREATION OF DATE RANGE section in coinbase_DB.py. Coinbase limits it to 300 candles per request so for example for minute data we can pull every 5 hours of data. (300 candles / 60 candles/hr = 5 Hours of candles). So change the second_time= date+pd.Timedelta("300 minute") to whatever you need. Please do not make a seperate DB for minute, hourly, etc. Just pull the base and aks ChatGPT or me and we can help you with the code. Now that you are ready just let the program run (ie coinbase_DB.py) . It will take a couple of days if you are getting multiple pairs from Coinbase for the first time. If it runs into a problem give it a couple of minutes of rest and start again. Happy Data gathering!!
