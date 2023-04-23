import random
from sre_parse import State
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


# Telegram bot token
TOKEN = 'Your telegram bot token here'

# Initialize bot and dispatcher instances
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Define the start command handler
@dp.message_handler(commands=['start'])
async def start_command_handler(message: types.Message):
    # Send a greeting message and prompt for bot function selection
    text = "Hello! I'm a simple Telegram bot. Please select a function."
    keyboard = InlineKeyboardMarkup(row_width=2)
    weather_button = InlineKeyboardButton('Current Weather', callback_data='weather')
    currency_button = InlineKeyboardButton('Currency Conversion', callback_data='currency')
    cute_animals_button = InlineKeyboardButton('Cute Animals', callback_data='animals')
    survey_button = InlineKeyboardButton('Create Survey', callback_data='survey')
    keyboard.add(weather_button, currency_button, cute_animals_button, survey_button)
    await message.reply(text, reply_markup=keyboard)

# Define the callback query handler for the weather button
@dp.callback_query_handler(lambda query: query.data == 'weather')
async def weather_callback_handler(query: types.CallbackQuery):
    # Ask user for the city name
    await bot.answer_callback_query(query.id)
    await bot.send_message(chat_id=query.message.chat.id, text="Please enter the city name:")

# Define the message handler for the city name
@dp.message_handler(lambda message: message.text and not message.text.startswith('/') and message.chat.type == 'private')
async def city_name_message_handler(message: types.Message):
    # Get the current weather in the specified city using the OpenWeatherMap API
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid= your weather api here'
        response = requests.get(url).json()
        weather_description = response['weather'][0]['description']
        temperature = response['main']['temp']
        temperature = round(temperature - 273.15, 2) # Convert from Kelvin to Celsius and round to 2 decimal places
        await message.reply(f"Current weather in {message.text}: {weather_description}. Temperature: {temperature}°C.")
    except Exception as e:
        print(e)
        await message.reply("Sorry, an error occurred while processing your request. Please try again later.")



# Define the states for the conversation
class CurrencyConversion(StatesGroup):
    BASE_CURRENCY = State()
    TARGET_CURRENCY = State()

# Define the callback query handler for the currency conversion button
@dp.callback_query_handler(lambda query: query.data == 'currency')
async def currency_callback_handler(query: types.CallbackQuery, state: FSMContext):
    # Ask user for the base currency and target currency
    await bot.answer_callback_query(query.id)
    await bot.send_message(chat_id=query.message.chat.id, text="Please enter the base currency (e.g. USD):")
    await CurrencyConversion.BASE_CURRENCY.set()


# Define the message handler for the base currency
@dp.message_handler(lambda message: message.chat.type == 'private', state=CurrencyConversion.BASE_CURRENCY)
async def base_currency_message_handler(message: types.Message, state: FSMContext):
    # Ask for the target currency
    base_currency = message.text.upper()
    try:
        await message.reply(f"Please enter the target currency (e.g. EUR):")
        await state.update_data(base_currency=base_currency)
        await CurrencyConversion.TARGET_CURRENCY.set()
    except:
        await message.reply("Sorry, that's an invalid currency code. Please try again.")

# Define the message handler for the target currency
@dp.message_handler(lambda message: message.chat.type == 'private', state=CurrencyConversion.TARGET_CURRENCY)
async def target_currency_message_handler(message: types.Message, state: FSMContext):
    # Convert the currency using the Exchange Rates API
    try:
        data = await state.get_data()
        base_currency = data.get('base_currency')
        target_currency = message.text.upper()
        url = f'https://api.exchangeratesapi.io/latest?base={base_currency}&symbols={target_currency}'
        response = requests.get(url).json()
        exchange_rate = response['rates'][target_currency]
        await message.reply(f"1 {base_currency} = {exchange_rate} {target_currency}")
    except:
        await message.reply("Sorry, that's an invalid currency code. Please try again.")
    finally:
        await state.finish()




# Initialize an in-memory cache
cache = {}

@dp.callback_query_handler(lambda query: query.data == 'animals')
async def animals_callback_handler(query: types.CallbackQuery):
    try:
        if 'photo_url' not in cache:
            url = 'https://api.thecatapi.com/v1/images/search'
            response = requests.get(url).json()
            photo_url = response[0]['url']
            cache['photo_url'] = photo_url
        else:
            photo_url = cache['photo_url']

        await bot.send_photo(chat_id=query.message.chat.id, photo=photo_url)
    except requests.exceptions.RequestException:
        await bot.send_message(chat_id=query.message.chat.id, text="Sorry, an error occurred while processing your request. Please try again later.")
    except KeyError:
        await bot.send_message(chat_id=query.message.chat.id, text="Sorry, an error occurred while processing your request. Please try again later.")



# Define the states for the conversation
class SurveyQuestions(StatesGroup):
    QUESTION = State()
    OPTIONS = State()

# Define the message handler for the survey questions
@dp.message_handler(lambda message: message.chat.type == 'group', state='*')
async def survey_question_message_handler(message: types.Message, state: FSMContext):
    question = message.text
    await state.update_data(question=question)
    await message.reply("Please enter the answer options for the survey, one by one. Type /done when you're finished.")
    await SurveyQuestions.OPTIONS.set()

# Define the message handler for the survey answer options
@dp.message_handler(commands=['done'], chat_type='group', state=SurveyQuestions.OPTIONS)
async def survey_options_message_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question = data.get('question')
    options = data.get('options', [])
    keyboard = InlineKeyboardMarkup(row_width=2)
    for option in options:
        button = InlineKeyboardButton(option, callback_data=f'survey_{question}_{option}')
        keyboard.add(button)
    await bot.send_message(chat_id=message.chat.id, text=question, reply_markup=keyboard)
    await state.finish()

# Define the message handler for survey answer options
@dp.message_handler(chat_type='group', state=SurveyQuestions.OPTIONS)
async def survey_options_handler(message: types.Message, state: FSMContext):
    options = state.data.get('options', [])
    options.append(message.text)
    await state.update_data(options=options)
    await message.reply('Option added. Please enter another option or type /done to finish.')


executor.start_polling(dp, skip_updates=True)




