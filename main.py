import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

# Load historical price data
data = pd.read_csv('SOL_historical_data_2024-02-01-2024-05-29.csv', parse_dates=['time'], index_col='time')

# Calculate pivot points, support, and resistance levels
data['Pivot'] = (data['high'].shift(1) + data['low'].shift(1) + data['close'].shift(1)) / 3
data['R1'] = 2 * data['Pivot'] - data['low'].shift(1)
data['S1'] = 2 * data['Pivot'] - data['high'].shift(1)
data['R2'] = data['Pivot'] + (data['high'].shift(1) - data['low'].shift(1))
data['S2'] = data['Pivot'] - (data['high'].shift(1) - data['low'].shift(1))

# Generate buy and sell signals
data['Buy_Signal'] = np.where(data['low'] <= data['S1'], 1, 0)
data['Sell_Signal'] = np.where(data['high'] >= data['R1'], 1, 0)

# Initialize positions
data['Position'] = np.where(data['Buy_Signal'], 1, np.where(data['Sell_Signal'], -1, 0))

# Output results
print(data[['close', 'Pivot', 'R1', 'S1', 'R2', 'S2', 'Buy_Signal', 'Sell_Signal', 'Position']])

data = data.dropna()

# Save results to a CSV file
data.to_csv('crypto_strategy_output.csv')

# Convert the date to numerical format for matplotlib
data['time'] = mdates.date2num(data.index.to_pydatetime())

# Create a new DataFrame for OHLC data
ohlc = data[['time', 'open', 'high', 'low', 'close']].copy()

# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot candlestick chart
candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)

# Plot pivot points, support, and resistance levels
ax.plot(data['time'], data['Pivot'], label='Pivot', color='orange', linestyle='-')
ax.plot(data['time'], data['R1'], label='R1', color='red', linestyle='--')
ax.plot(data['time'], data['S1'], label='S1', color='green', linestyle='--')
ax.plot(data['time'], data['R2'], label='R2', color='red', linestyle=':')
ax.plot(data['time'], data['S2'], label='S2', color='green', linestyle=':')

# Plot buy signals
buy_signals = data[data['Buy_Signal'] == 1]
ax.scatter(buy_signals['time'], buy_signals['close'], label='Buy Signal', color='blue', marker='^', s=100, zorder=3)

# Plot sell signals
sell_signals = data[data['Sell_Signal'] == 1]
ax.scatter(sell_signals['time'], sell_signals['close'], label='Sell Signal', color='purple', marker='v', s=100, zorder=3)

# Formatting
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45)
plt.title('Pivot Point Strategy with Supply and Demand Zones')
plt.xlabel('time')
plt.ylabel('Price')
plt.legend()
plt.grid()
plt.tight_layout()

# Show plot
plt.show()