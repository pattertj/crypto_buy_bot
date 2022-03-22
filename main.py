from bot import Bot

# Build our bot
bot = Bot()

# Build our shopping list in USD
bot.shopping_list = {"BTC": 0.0, "ETH": 0.0}

# Checkout
bot.checkout()