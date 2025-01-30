from histdata import TvDatafeed, Interval
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn


app = FastAPI()

data_store = {}


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
