# telegram-multipurpose-bot

This Python script generates a straightforward Telegram bot that enables users to carry out a number of tasks like checking the weather, converting currencies, and watching adorable animals. A simple in-memory cache is used to store data, along with requests to get data from third-party APIs like OpenWeatherMap and TheCatAPI. The script uses the aiogram library to manage the bot's interactions with the user and the Telegram API.

# Setup

1.Install the required libraries listed in the script by running the following command:
   pip install aiogram requests sre-parse
2.Create a Telegram bot and obtain its API token by following the instructions in the Telegram documentation.
3.Obtain an API key from OpenWeatherMap and replace your weather api here in the script with the API key.
4.Replace Your telegram bot token here in the script with the API token of your Telegram bot.
5.Run the script using python <script_name>.py.

# Usage 
Users can communicate with the bot on Telegram by sending commands and messages once it is operational. There are the following capabilities:

1.Sends a welcome message and asks the user to choose a function with /start.

2.Shows the current weather in the chosen city under Current Weather. The user is asked to type the name of the city.

3.Currency Conversion: Uses the Exchange Rates API to convert a certain amount of a base currency to a destination currency. The base currency and target currency must both be entered by the user.

4.Using the TheCatAPI, the Cute Animals page shows a random image of a cute animal.

5.Create Survey: This forms a survey after asking user to put questions and options
