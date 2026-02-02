import yfinance as yf
from modules.chartist import Chartist

# Validation Script: "What if we bought 3 months ago?"
print("=== Historical Validation: 2330.TW (3 Months Ago) ===")

ticker = "2330.TW"
# 1. Get Historical Price
df = yf.download(ticker, period="6mo", interval="1d", progress=False)
if df.empty:
    print("Error: No data.")
    exit()

# Flatten MultiIndex
if hasattr(df.columns, 'get_level_values'):
    df.columns = df.columns.get_level_values(0)

# Pick a date ~3 months ago (approx 60 trading days)
past_idx = -60
if len(df) < 60:
    print("Not enough history.")
    exit()

past_row = df.iloc[past_idx]
past_date = past_row.name.strftime('%Y-%m-%d')
past_close = float(past_row['Close'])

# Current Price
curr_close = float(df.iloc[-1]['Close'])

print(f"Date: {past_date}")
print(f"Past Price: {past_close}")
print(f"Current Price: {curr_close}")

roi = (curr_close - past_close) / past_close * 100
print(f"Actual ROI (Buy & Hold): {roi:.2f}%")

# Simulation: Would Chartist have bought then?
# We slice the dataframe to simulate 'past' state
# RSI Calculation on sliced data
import pandas_ta as ta
df_past = df.iloc[:past_idx+1].copy()
df_past['RSI'] = df_past.ta.rsi(length=14)
past_rsi = df_past.iloc[-1]['RSI']

print(f"Technical Indicator at that time (RSI): {past_rsi:.2f}")

if past_rsi < 30:
    print("Alpha Assessment: OVERSOLD (Strong Buy Signal)")
elif past_rsi > 70:
    print("Alpha Assessment: OVERBOUGHT (Sell Signal)")
else:
    print("Alpha Assessment: NEUTRAL")

print("=============================================")
