# ```crypto_buy_bot```: A simple script for buying crypto

```crypto_buy_bot``` was a script I threw together to help simplify my monthly crypto DCA deposits. It's intended to be run from the command line, howevr, the bot does also support .env for storing your exchange credentials.

To get started using ```crypto_buy_bot```, run the following in your terminal:

```python
# Clone crypto_buy_bot
git clone https://github.com/pattertj/crypto_buy_bot.git

# Run Crypto_Buy_Bot
pipenv run main.py
```

To get up and running for development, additionally run:

```python
# Install dependencies
pipenv install --dev

# Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
```
