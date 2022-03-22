import attr
import os
import sys
from dotenv import load_dotenv
from os import getenv
from ccxt import Exchange

load_dotenv()

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(f'{root}/python')

import ccxt  # noqa: E402

@attr.s(auto_attribs=True)
class Bot():
    shopping_list: dict = attr.ib(validator=attr.validators.instance_of(dict), init=False)
    exchange: super(Exchange) = attr.ib(validator=attr.validators.instance_of(super(Exchange)), init=False)
        
    def __attrs_post_init__(self):
        exchange_id = getenv("EXCHANGE_ID")

        if exchange_id is None:
            exchange_class = self.prompt_for_exchanges()
        else:
            try:
                exchange_class = getattr(ccxt, exchange_id)
            except:
                print("Invalid exchange.")
                exchange_class = self.prompt_for_exchanges()

        self.exchange = exchange_class({
            'apiKey': getenv("API_KEY"),
            'secret': getenv("API_SECRET"),
            'password': getenv("API_PASSWORD"),
            'verbose': False,
        })
    
    def checkout(self):
        # Get Balances
        if not self.exchange.has['fetchBalance']:
            print("Sorry, this exchange doesn't support fetchBalance.")
            return
        
        balances = self.exchange.fetch_balance()
        usd_balance = round(balances['USD']['total'], 2)

        # Get total purchase amount
        total_buy = sum(self.shopping_list.values())

        print("You will purchase:")
        for coin, amount in self.shopping_list.items():
            print(f"- ${amount} of {coin}." )

        print(f"Your available USD balance is: ${usd_balance}")
        print(f"Your total purchase amount is: ${total_buy}")

        # Check if we have enough to pay.
        if usd_balance < total_buy:
            print("You have insufficient funds for this purchase. Please remove some items from your cart.")
            return

        print("Are you ready to checkout? [y/n]")
        go_on = input()

        if go_on not in ["y", "Y"]:
            print("Exiting now.")
            return

        print("Beginning purchases...")

        self.process_payment()

        print("Payment Complete. Please remember to take your items. Have a nice day!")

    def process_payment(self):
        coin: str
        amount: float
        for coin, amount in self.shopping_list.items():
            # Build Symbol
            symbol = f"{coin}/USD"

            # Get Coin Details
            if not self.exchange.has['fetchTickers']:
                print("Sorry, this exchange doesn't support fetchTickers.")
                return
            
            ticker = self.exchange.fetch_tickers([symbol])

            print(f"{coin} Market Price: ${ticker[symbol]['last']}")

            # Calculate amount of coin to buy
            amount_in_coin = amount / ticker[symbol]['last']

            print(f"${amount} of {coin} is {amount_in_coin}{coin}.")  

            # Place market order
            self.exchange.create_market_buy_order(symbol=symbol, amount=amount_in_coin)

            print(f"Market buy order for {coin}, completed.")
            
    def prompt_for_exchanges(self) -> Exchange:
        # Get the exchange input
        print("Please Select an Exchange:")
        
        for ex in ccxt.exchanges:
            print(ex)
        
        exchange_name = input()
        
        # Try to parse the input
        try:
            exchange_class = getattr(ccxt, exchange_name)
        except:
            print("Invalid exchange.")
            return self.prompt_for_exchanges()
        
        # Return if successful
        return exchange_class