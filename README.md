# Binance Auto Trading Bot

This Python script automates cryptocurrency trading on Binance using the `ccxt` library. It follows a simple strategy of buying and selling based on price percentage changes.

## Features
- Fetches market data from Binance.
- Allows user input for trading pair, amount, and percentage triggers.
- Implements a simple buy-low, sell-high strategy.
- Handles API errors and logs trade actions.

## Requirements
- Python 3.x
- `ccxt` library

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/binance-auto-trade.git
   cd binance-auto-trade
   ```
2. Install dependencies:
   ```sh
   pip install ccxt
   ```
3. Set up your API keys in the script:
   ```python
   exchange = ccxt.binance({
       'apiKey': 'your_api_key',  # Replace with your API key
       'secret': 'your_secret_key',  # Replace with your secret key
       'enableRateLimit': True,
   })
   ```

## Usage
1. Run the script:
   ```sh
   python trading_bot.py
   ```
2. Enter trading details when prompted (symbol, amount, percentage triggers).
3. The bot will execute trades based on price changes.

## Disclaimer
This script is for educational purposes only. Use it at your own risk. Trading cryptocurrencies involves significant risk.

## License
MIT License
