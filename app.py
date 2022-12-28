from aiogram import Bot, Dispatcher, executor, types
import requests
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('API_KEY'))
dp = Dispatcher(bot)
admin = 766712553

whitelist = [admin]
approved = lambda message: message.from_user.id in whitelist
guest = lambda message: message.from_user.id not in whitelist


async def to_database(from_chat_id, username, message):
    await bot.send_message(
        -1001833854389,
        f"{message}\n\nСообщение от @{username}\nID: " f"`{from_chat_id}`",
        parse_mode="MARKDOWN",
    )


@dp.message_handler(commands="whitelist")
async def check_wl(message: types.Message):
    await bot.send_message(
        message.chat.id, f"Количество людей с правами доступа: {len(whitelist)}"
    )
    await to_database(message.chat.id, message.chat.username, message.text)


@dp.message_handler(commands="access")
async def check_access(message: types.Message):
    if message.from_user.id in whitelist:
        await bot.send_message(message.chat.id, "У вас есть доступ")
    else:
        await bot.send_message(message.chat.id, "У вас нету доступа")
    await to_database(message.chat.id, message.chat.username, message.text)


@dp.message_handler(commands="chatid")
async def get_user_id(message: types.Message):
    await message.reply(
        f"Ваш уникальный ID: `{message.from_user.id}`", parse_mode="MARKDOWN"
    )
    await to_database(message.chat.id, message.chat.username, message.text)


@dp.message_handler(approved, commands="start")
async def info_for_approved(message: types.Message):
    await message.reply("Введите ваш вопрос:")
    await to_database(message.chat.id, message.chat.username, message.text)


@dp.message_handler(guest, commands="start")
async def info_for_guests(message: types.Message):
    await message.reply(
        f"Сначало получите доступ у администратора (@lighteezy)"
        f"\nПроверить доступ: /access"
    )
    await to_database(message.chat.id, message.chat.username, message.text)

@dp.message_handler(approved, content_types='text')
async def search(message: types.Message):
    url = 'https://pomahach.com/search/'
    query = message.text
    payload = {'gsc.tab': '0', 'gsc.q': query, 'gsc.sort': ''}
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        results = response.json()
        message_text = f'Here are the search results for "{query}":\n'
        for result in results:
            message_text += f'- {result["gs-title"]}\n'
        await message.reply(message_text)
    else:
        await message.reply(f'Sorry, there was an error processing your search. Please try again later.{response}')
    await to_database(message.chat.id, message.chat.username, message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
