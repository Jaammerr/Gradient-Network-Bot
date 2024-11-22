import logging
from aiogram import Bot, Dispatcher
from core.telegram_bot.handlers import register_handlers

class TelegramBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

    async def start(self):

        register_handlers(self.dp)
        await self.dp.start_polling(self.bot)