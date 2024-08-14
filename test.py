from histdata import TvDatafeed, Interval
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

data_store = {}

@app.get("/")
async def root():
    return {"message": "Hello World"}
    
@app.get("/fastapi/get-hist/pass==cheeku/{ticker}")
async def get_history(ticker: str):
    try:
        tv = TvDatafeed()
        data_store[ticker] = ticker
        nifty_index_data = tv.get_hist(symbol=ticker, exchange='NSE', interval=Interval.in_1_minute, n_bars=10000)

        df = pd.DataFrame(nifty_index_data)

        json_data = df.to_json(orient='records')
        # Convert JSON string to a Python list
        json_data = pd.read_json(json_data).to_dict(orient='records')

        return JSONResponse(content=json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/fastapi/get-stored-data/pass==cheeku")
async def get_stored_data():
    return JSONResponse(content={"stored_tickers": list(data_store.values())})


if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0", port=8080)
