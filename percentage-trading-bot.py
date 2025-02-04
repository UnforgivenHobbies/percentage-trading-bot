import ccxt
import time
import logging

logging.basicConfig(filename='script.log', level=logging.INFO, format='%(asctime)s - %(message)s')

logging.info('Script started')
# Initialize the exchange
exchange = ccxt.binance({
    'apiKey': '',  # Replace with your API key
    'secret': '',  # Replace with your secret key
    'enableRateLimit': True,
})

# Prefilled values
DEFAULT_SYMBOL = "BTC/USDC"
DEFAULT_AMOUNT = 0.0001
DEFAULT_PERCENTAGE = 1  # Default percentage for buy/sell triggers

# Global variables
min_notional_error_shown = False
min_notional_filter_error_shown = False

# Function to get user input with prefilled values
def get_user_input():
    # Prompt for symbol
    symbol = (
        input(f"Enter the trading pair (e.g., BTC/USDC) [Default: {DEFAULT_SYMBOL}]: ")
        .strip()
        .upper()
    )
    if not symbol:  # If the user hits Enter, use the default value
        symbol = DEFAULT_SYMBOL

    # Prompt for amount
    amount_input = input(
        f"Enter the amount to trade (e.g., 0.0001) [Default: {DEFAULT_AMOUNT}]: "
    ).strip()
    if not amount_input:  # If the user hits Enter, use the default value
        amount = DEFAULT_AMOUNT
    else:
        amount = float(amount_input)

    # Prompt for percentage
    percentage_input = input(
        f"Enter the percentage for buy/sell triggers (e.g., 1) [Default: {DEFAULT_PERCENTAGE}%]: "
    ).strip()
    if not percentage_input:  # If the user hits Enter, use the default value
        percentage = DEFAULT_PERCENTAGE
    else:
        percentage = float(percentage_input)

    return symbol, amount, percentage

# Get user input for symbol, amount, and percentage
symbol, amount, percentage = get_user_input()

# Variables to store the last action, price, and desired trigger prices
last_action = None  # Can be 'buy' or 'sell'
last_price = None  # Price of the last buy/sell action
desired_buy_price = None  # Price at which to trigger a buy
desired_sell_price = None  # Price at which to trigger a sell

def get_min_notional(symbol):
    markets = exchange.load_markets()
    market = markets.get(symbol)

    if market is None:
        print(f"Error: Market data for {symbol} not found.")
        global min_notional_error_shown  # Ensure this variable is declared globally if used
        if not min_notional_filter_error_shown:
            print(f"Warning: MIN_NOTIONAL filter not found for {symbol}.")
            min_notional_filter_error_shown = True
        return None
    for filter in market.get("info", {}).get("filters", []):
        if filter.get("filterType") == "MIN_NOTIONAL":
            min_notional = filter.get("minNotional")
            if min_notional is not None:
                return float(min_notional)

    return None

def calculate_min_amount(symbol, min_notional):
    current_price = get_price(symbol)

    if min_notional is None:
        global min_notional_error_shown
        if not min_notional_error_shown:
            print(f"Warning: min_notional is None for {symbol}. Using default amount.")
            min_notional_error_shown = True
        return amount  # Fallback to initial amount

    if current_price is None or current_price == 0:
        print(f"Warning: current_price is None or 0 for {symbol}. Using default amount.")
        return amount  # Avoid division by zero

    return min_notional / current_price

def get_balance(currency):
    balance = exchange.fetch_balance()
    return balance["total"][currency]

def get_price(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker.get("last", None)
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
    return None

def place_order(symbol, amount, side):
    try:
        order = exchange.create_order(symbol, "market", side, amount)
        return order
    except Exception as e:
        print(f"Error placing {side} order for {symbol}: {e}")
    return None

def trading_strategy():
    global last_action, last_price, desired_buy_price, desired_sell_price

    current_price = get_price(symbol)

    # Fetch minimum notional value and adjust amount
    min_notional = get_min_notional(symbol)
    min_amount = calculate_min_amount(symbol, min_notional)

    if min_amount is None or min_amount <= 0:
        print(f"Error: Invalid min_amount ({min_amount}) for {symbol}. Skipping trade.")
        return

    adjusted_amount = max(amount, min_amount)

    if last_action is None:
        # First run: Sell immediately
        print(f"Initial sell: Selling {adjusted_amount} {symbol} at {current_price}.")
        logging.info(f"Initial sell: Selling {adjusted_amount} {symbol} at {current_price}.")
        place_order(symbol, adjusted_amount, "sell")
        last_action = "sell"
        last_price = current_price
        desired_buy_price = current_price * (1 - percentage / 100)  # Set desired buy price (percentage below sell price)
        print(f"Desired buy price set to: {desired_buy_price}")
        logging.info(f"Desired buy price set to: {desired_buy_price}")
    elif last_action == "sell":
        # After selling: Check if price dropped to desired buy price
        if current_price <= desired_buy_price:
            print(f"Price reached desired buy price. Buying {adjusted_amount} {symbol} at {current_price}.")
            logging.info(f"Price reached desired buy price. Buying {adjusted_amount} {symbol} at {current_price}.")
            place_order(symbol, adjusted_amount, "buy")
            last_action = "buy"
            last_price = current_price
            desired_sell_price = current_price * (1 + percentage / 100)  # Set desired sell price (percentage above buy price)
            print(f"Desired sell price set to: {desired_sell_price}")
            logging.info(f"Desired sell price set to: {desired_sell_price}")
        else:
            print(f"Waiting to buy. Current price: {current_price}, Desired buy price: {desired_buy_price}")
    elif last_action == "buy":
        # After buying: Check if price rose to desired sell price
        if current_price >= desired_sell_price:
            print(f"Price reached desired sell price. Selling {adjusted_amount} {symbol} at {current_price}.")
            logging.info(f"Price reached desired sell price. Selling {adjusted_amount} {symbol} at {current_price}.")
            place_order(symbol, adjusted_amount, "sell")
            last_action = "sell"
            last_price = current_price
            desired_buy_price = current_price * (1 - percentage / 100)  # Set desired buy price (percentage below sell price)
            print(f"Desired buy price set to: {desired_buy_price}")
            logging.info(f"Desired buy price set to: {desired_buy_price}")
        else:
            print(f"Waiting to sell. Current price: {current_price}, Desired sell price: {desired_sell_price}")

if __name__ == "__main__":
    print("Starting trading bot...")
    while True:
        try:
            trading_strategy()
            time.sleep(5)  # Run the strategy every 5 seconds
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)  # Wait before retrying
            logging.info('Script finished')