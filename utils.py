import requests
from datetime import datetime, timedelta
import pandas as pd
import time

# Create a session for HTTP requests
session = requests.Session()
session.headers.update({
    'Content-Type': 'application/json',
    'User-Agent': 'Python http.client'
})

def get_json_response(url):
    """Utility function to send GET request and return JSON response."""
    try:
        response = session.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
def check_data_availability(token):
    """Check if there is data available for the given token."""
    today = datetime.now().strftime('%Y-%m-%d')
    url = f'https://api.exchange.coinbase.com/products/{token}-USD/candles?start={today}&end={today}&granularity=86400'
    candles = get_json_response(url)
    return bool(candles)
    
def find_start_date(token):
    """Find the earliest date with data available for the given token."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 5)  # Start 5 years ago

    print(start_date)

    for _ in range(5):  # Limit to 5 iterations
        if start_date >= end_date:
            break
        url = f'https://api.exchange.coinbase.com/products/{token}-USD/candles?start={start_date.strftime("%Y-%m-%d")}&end={end_date.strftime("%Y-%m-%d")}&granularity=86400'
        data = get_json_response(url)
        if data:
            return start_date
        start_date += timedelta(days=365)  # Move back another year

    return None
    
def process_response(data):
    """Convert API response data to a pandas DataFrame."""
    if not data or not isinstance(data, list) or len(data[0]) != 6:
        return pd.DataFrame()
    try:
        df = pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    except Exception as e:
        print(f"Error processing data: {e}")
        return pd.DataFrame()

def process_token(token, start_date, end_date, max_interval=timedelta(days=90)):
    """Process data for a single token within a date range."""
   
    url = f'https://api.exchange.coinbase.com/products/{token}-USD/candles?start={start_date.strftime("%Y-%m-%d")}&end={end_date.strftime("%Y-%m-%d")}&granularity=86400'
    candles = get_json_response(url)

    df = process_response(candles)
    if not df.empty:
        df['token'] = token

    return df 

default_start_date = datetime.strptime('2024-02-01', '%Y-%m-%d')
default_end_date = datetime.now()

def main(token):
    token_df = process_token(token, default_start_date, default_end_date)

    # Save the master DataFrame to a CSV file
    token_df.to_csv(f'{token}_historical_data_{default_start_date.strftime("%Y-%m-%d")}-{default_end_date.strftime("%Y-%m-%d")}.csv', index=False)

    return f'{token}_historical_data_{default_start_date.strftime("%Y-%m-%d")}-{default_end_date.strftime("%Y-%m-%d")}.csv'

