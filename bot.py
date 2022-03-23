import os
import sys
from os import getenv

import attr
from ccxt import Exchange
from dotenv import load_dotenv

load_dotenv()

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(f"{root}/python")

import ccxt  # noqa: E402


@attr.s(auto_attribs=True)
class Bot:
    shopping_list: dict = attr.ib(
        validator=attr.validators.instance_of(dict), init=False, default={}
    )
    exchange: Exchange = attr.ib(
        validator=attr.validators.instance_of(Exchange), init=False
    )

    def __attrs_post_init__(self):
        """Upon creation, setup our exchange."""

        # Check our .env file first
        exchange_id = getenv("EXCHANGE_ID")

        # Check the class
        exchange_class = self.get_exchange_class(exchange_id)

        api_key = self.get_or_ask_for("API_KEY")
        api_secret = self.get_or_ask_for("API_SECRET")
        api_password = self.get_or_ask_for("API_PASSWORD")

        # Build the exchange
        self.exchange = exchange_class(
            {
                "apiKey": api_key,
                "secret": api_secret,
                "password": api_password,
                "verbose": False,
            }
        )

    def checkout(self) -> None:
        """Main entry into the logic of the bot."""

        # Build our shopping list if needed.
        if self.shopping_list is None or self.shopping_list == {}:
            self.build_shopping_list()

        # Get Balances
        if not self.exchange.has["fetchBalance"]:
            print("Sorry, this exchange doesn't support fetchBalance.")
            return

        balances = self.exchange.fetch_balance()
        usd_balance = round(balances["USD"]["total"], 2)

        # Get total purchase amount
        total_buy = sum(self.shopping_list.values())

        print("You are trying to purchase:")
        for coin, amount in self.shopping_list.items():
            print(f"- ${amount} of {coin}.")

        print(f"Your available USD balance is: ${usd_balance}")
        print(f"Your total purchase amount is: ${total_buy}")

        # Check if we have enough to pay.
        if usd_balance < total_buy:
            print(
                "You have insufficient funds for this purchase. Please remove some items from your cart."
            )
            return

        print("Are you ready to checkout? [y/n]")
        go_on = input()

        if go_on not in ["y", "Y"]:
            print("Exiting now.")
            return

        print("Beginning purchases...")

        self.process_payment()

        print("Payment Complete. Please remember to take your items. Have a nice day!")

    def process_payment(self) -> None:
        coin: str
        amount: float
        for coin, amount in self.shopping_list.items():
            # Build Symbol
            symbol = f"{coin}/USD"

            # Get Coin Details
            if not self.exchange.has["fetchTickers"]:
                print("Sorry, this exchange doesn't support fetchTickers.")
                return

            ticker = self.exchange.fetch_tickers([symbol])

            print(f"{coin} Market Price: ${ticker[symbol]['last']}")

            # Calculate amount of coin to buy
            amount_in_coin = amount / ticker[symbol]["last"]

            print(f"${amount} of {coin} is {amount_in_coin}{coin}.")

            if not self.exchange.has["createOrder"]:
                print("Sorry, this exchange doesn't support createOrder.")
                return

            # Place market order
            try:
                self.exchange.create_market_buy_order(
                    symbol=symbol, amount=amount_in_coin
                )
            except Exception:
                print(
                    "An error occurred placing your market order. Please check your account."
                )
                return

            print(f"Market buy order for {coin}, completed.")

    def get_exchange_class(self, exchange_id):
        if exchange_id is None:
            exchange_class = self.prompt_for_exchanges()
        else:
            try:
                exchange_class = getattr(ccxt, exchange_id)
            except Exception:
                print("Invalid exchange.")
                exchange_class = self.prompt_for_exchanges()
        return exchange_class

    def prompt_for_exchanges(self):
        # Get the exchange input
        print("Please Select an Exchange:")

        for ex in ccxt.exchanges:
            print(ex)

        exchange_name = input()

        # Try to parse the input
        try:
            exchange_class = getattr(ccxt, exchange_name)
        except Exception:
            print("Invalid exchange.")
            return self.prompt_for_exchanges()

        # Return if successful
        return exchange_class

    def build_shopping_list(self) -> None:
        print("What coin do you want to buy?")
        coin = str(input())
        print("How much in USD do you want to buy?")
        amount = float(input())

        self.shopping_list[coin] = amount

        print("Coin added, do you want to buy another? [y/n]")
        go_on = input()

        if go_on in ["y", "Y"]:
            self.build_shopping_list()

        return

    @staticmethod
    def get_or_ask_for(key: str) -> str:
        # Check our .env file first
        value = getenv(key)

        # If we have a value, return it.
        if value is not None:
            return value

        # If not, prompt for it.
        print(
            f"Please enter your {key}. It will not be stored locally, only in memory."
        )
        return input()
