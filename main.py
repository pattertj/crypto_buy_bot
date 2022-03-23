from bot import Bot

# Build our bot
bot = Bot()

# Build our shopping dict in USD {"BTC": 0.0, "ETH": 0.0}
bot.shopping_list = {}

# Checkout
bot.checkout()
