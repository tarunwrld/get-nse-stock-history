# from histdata import TvDatafeed, Interval
# import pandas as pd
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# import uvicorn
# from nse import NSE


# app = FastAPI()

# data_store = {}


# nse = NSE()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
    
# @app.get("/fastapi/get-hist/pass==cheeku/{ticker}/{interval}/{n_bars}")
# async def get_history(ticker: str, interval: int, n_bars: int):
#     try:
#         tv = TvDatafeed()
#         data_store[ticker] = ticker
        
#         interval_mapping = {
#             1: Interval.in_1_minute,
#             3: Interval.in_3_minute,
#             5: Interval.in_5_minute,
#             15: Interval.in_15_minute,
#             30: Interval.in_30_minute,
#             60: Interval.in_1_hour,
#             240: Interval.in_4_hour,
#             1440: Interval.in_daily,
#             10080: Interval.in_weekly,
#             43200: Interval.in_monthly
#         }
        
#         if interval not in interval_mapping:
#             raise HTTPException(status_code=400, detail="Invalid interval")

#         nifty_index_data = tv.get_hist(symbol=ticker, exchange='NSE', interval=interval_mapping[interval], n_bars=n_bars)

#         df = pd.DataFrame(nifty_index_data)

#         json_data = df.to_json(orient='records')
#         json_data = pd.read_json(json_data).to_dict(orient='records')

#         return JSONResponse(content=json_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.get("/fastapi/get-nse-hist/{ticker}/{n_bars}")
# async def get_history(ticker: str, n_bars: int):
#     try:
#         data_store[ticker] = ticker
#         # Fetch historical data for the given ticker and interval
#         data = nse.getHistoricalData(ticker, "EQ", n_bars)
#         if data is None:
#             raise HTTPException(status_code=404, detail="Data not found for the given ticker")
#         return JSONResponse(content=data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.get("/fastapi/get-stored-data/pass==cheeku")
# async def get_stored_data():
#     return JSONResponse(content={"stored_tickers": list(data_store.values())})


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)
from histdata import TvDatafeed, Interval
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from nse import NSE


app = FastAPI()

data_store = {}


class NSE():
    def __init__(self, timeout=10):
        self.base_url = 'https://www.nseindia.com'
        self.session = requests.sessions.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9"
        }
        self.timeout = timeout
        self.session.get(self.base_url, timeout=timeout)

    def getHistoricalData(self, symbol, series, days):
        try:
            # Calculate the 'from_date' based on current date and the specified number of days
            to_date = datetime.today().date()
            from_date = to_date - timedelta(days=days)
            
            url = "/api/historical/cm/equity?symbol={0}&series=[%22{1}%22]&from={2}&to={3}&csv=true".format(
                symbol.replace('&', '%26'), series, from_date.strftime('%d-%m-%Y'), to_date.strftime('%d-%m-%Y'))
            r = self.session.get(self.base_url + url, timeout=self.timeout)
            df = pd.read_csv(BytesIO(r.content), sep=',', thousands=',')
            
            df = df.rename(columns={'Date ': 'date', 'series ': 'series', 'OPEN ': 'open', 'HIGH ': 'high', 'LOW ': 'low', 
                                     'PREV. CLOSE ': 'prev_close', 'ltp ': 'ltp', 'close ': 'close', 
                                     '52W H ': 'hi_52_wk', '52W L ': 'lo_52_wk', 'VOLUME ': 'trdqty', 
                                     'VALUE ': 'trdval', 'No of trades ': 'trades'})
            df.date = pd.to_datetime(df.date).dt.strftime('%Y-%m-%d')
            
            json_data = df.to_dict(orient='records')
            
            return json_data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

nse = NSE()

@app.get("/")
async def root():
    return {"message": "Hello World"}
    
@app.get("/fastapi/get-hist/pass==cheeku/{ticker}/{interval}/{n_bars}")
async def get_history(ticker: str, interval: int, n_bars: int):
    try:
        tv = TvDatafeed()
        data_store[ticker] = ticker
        
        interval_mapping = {
            1: Interval.in_1_minute,
            3: Interval.in_3_minute,
            5: Interval.in_5_minute,
            15: Interval.in_15_minute,
            30: Interval.in_30_minute,
            60: Interval.in_1_hour,
            240: Interval.in_4_hour,
            1440: Interval.in_daily,
            10080: Interval.in_weekly,
            43200: Interval.in_monthly
        }
        
        if interval not in interval_mapping:
            raise HTTPException(status_code=400, detail="Invalid interval")

        nifty_index_data = tv.get_hist(symbol=ticker, exchange='NSE', interval=interval_mapping[interval], n_bars=n_bars)

        df = pd.DataFrame(nifty_index_data)

        json_data = df.to_json(orient='records')
        json_data = pd.read_json(json_data).to_dict(orient='records')

        return JSONResponse(content=json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/fastapi/get-nse-hist/{ticker}/{n_bars}")
async def get_history(ticker: str, n_bars: int):
    try:
        data_store[ticker] = ticker
        # Fetch historical data for the given ticker and interval
        data = nse.getHistoricalData(ticker, "EQ", n_bars)
        if data is None:
            raise HTTPException(status_code=404, detail="Data not found for the given ticker")
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/fastapi/get-stored-data/pass==cheeku")
async def get_stored_data():
    return JSONResponse(content={"stored_tickers": list(data_store.values())})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
