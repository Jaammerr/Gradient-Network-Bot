from aiogram import Router, types, F, Bot
from database import (
    get_user_accounts,
    get_user_proxies
)
from core.telegram_bot.keyboards import main_menu_keyboard
from core.bot import Bot
from core.telegram_bot.shared import user_bot, user_tasks
import asyncio

router = Router()

@router.callback_query(F.data == 'action_farm')
async def start_stop_mining(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    if user_id in user_tasks:
        bot = user_bot[user_id]
        await bot.stop()
        task = user_tasks[user_id]
        task.cancel()
        del user_tasks[user_id]
        del user_bot[user_id]
        await callback_query.answer("Farming stopped", show_alert=False)
        await callback_query.message.edit_reply_markup(reply_markup=main_menu_keyboard(user_id))
    else:

        accounts = get_user_accounts(user_id)
        proxies = get_user_proxies(user_id)

        if not accounts:
            await callback_query.answer("You have no added accounts or your accounts are not registered add or register accounts first", show_alert=True)
            return

        if not proxies:
            await callback_query.answer("You have no added proxies add proxies first", show_alert=True)
            return

        if len(proxies) < len(accounts):
            await callback_query.answer("The number of proxies is less than the number of accounts add more proxies", show_alert=True)
            return

        bot = Bot(user_id, accounts, proxies)

        user_bot[user_id] = bot
        task = asyncio.create_task(bot.farm_process())
        user_tasks[user_id] = task
        await callback_query.answer("Farm started", show_alert=False)
        await callback_query.message.edit_reply_markup(reply_markup=main_menu_keyboard(user_id))
