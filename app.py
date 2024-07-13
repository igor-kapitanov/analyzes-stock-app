from flask import Flask, render_template, request
import requests
import pandas as pd

app = Flask(__name__)

API_KEY = '5MU3Y87Z0CMTZ72Q'

def fetch_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    # Check if the response contains 'Time Series (Daily)'
    if 'Time Series (Daily)' in data:
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df = df.apply(pd.to_numeric)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        df['SMA_20'] = df['4. close'].rolling(window=20).mean()
        df['SMA_50'] = df['4. close'].rolling(window=50).mean()
        df['Trend'] = df['SMA_20'] > df['SMA_50']
        return df
    else:
        # Return an empty DataFrame and an error message if the key is not found
        return pd.DataFrame(), data.get('Error Message', 'Unknown error occurred')

@app.route('/', methods=['GET', 'POST'])
def index():
    stock_data = None
    error_message = None
    symbol = ''
    if request.method == 'POST':
        symbol = request.form['symbol']
        stock_data, error_message = fetch_stock_data(symbol)
    return render_template('index.html', stock_data=stock_data, symbol=symbol, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
