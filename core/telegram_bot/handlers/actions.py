from aiogram import Router, types, F, Bot
from core.telegram_bot.handlers.register_accounts import register_accounts_start
from core.telegram_bot.handlers.start_stop_mining import start_stop_mining

router = Router()


@router.callback_query(F.data == "action_registration")
async def action_registration(callback_query: types.CallbackQuery, bot: Bot):
    await register_accounts_start(callback_query, bot)


@router.callback_query(F.data == "action_mining")
async def action_mining(callback_query: types.CallbackQuery, bot: Bot):
    await start_stop_mining(callback_query, bot)
