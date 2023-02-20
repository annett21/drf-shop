from django.conf import settings
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

from django.core.management.base import BaseCommand
import logging
import time
from asgiref.sync import sync_to_async
from ...models import Category, Producer


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_API_TOKEN)

dp = Dispatcher(bot)

button = KeyboardButton("Categories")
button_producers = KeyboardButton("Producers")

keybord = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

keybord.add(button)
keybord.add(button_producers)


@dp.message_handler(commands=["help", "start"])
async def command_help(message: types.Message):
    await message.answer("Input some message", reply_markup=keybord)


@sync_to_async
def get_categories():
    return list(Category.objects.all())


@dp.message_handler(lambda message: message.text == "Categories")
async def certain_message(msg: types.Message):
    categories = await get_categories()

    msg_to_answer = ""
    for cat in categories:
        msg_to_answer += f"Category: {cat.name}\n{cat.description}\n"
    await bot.send_message(msg.from_user.id, msg_to_answer)


@sync_to_async
def get_producers():
    return list(Producer.objects.all())


@dp.message_handler(lambda message: message.text == "Producers")
async def producers_callback(msg: types.Message):
    producers = await get_producers()

    msg_to_answer = ""
    for producer in producers:
        msg_to_answer += f"Producer: {producer.name}\n"
    await bot.send_message(msg.from_user.id, msg_to_answer)


@dp.message_handler()
async def query_telegram(msg: types.Message):
    print(msg.text)
    await bot.send_message(msg.chat.id, "Understandable. Have a nice day")


class Command(BaseCommand):
    help = "Test TG bot"

    def handle(self, *args, **options):
        executor.start_polling(dp)
        