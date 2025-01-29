import requests
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

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
