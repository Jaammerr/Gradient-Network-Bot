from aiogram import Router, types, F, Bot
from database import (
    get_user_accounts_for_register,
    get_user_proxies,
    get_user_captcha_service_and_key,
)
from core import Bot
from core.telegram_bot.keyboards import main_menu_keyboard
from core.telegram_bot.shared import disable

router = Router()

@router.callback_query(F.data == 'action_registration')
async def register_accounts_start(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    accounts = get_user_accounts_for_register(user_id)
    proxies = get_user_proxies(user_id)
    captcha = get_user_captcha_service_and_key(user_id)

    if captcha:
        captcha_service, captcha_api_key = captcha['service'], captcha['api_key']

    if not accounts:
        await callback_query.answer("You have no added accounts or your all accounts already registered add new accounts first", show_alert=True)
        return
    if not proxies:
        await callback_query.answer("You have no added proxies add proxy first", show_alert=True)
        return
    if len(proxies) < len(accounts):
        await callback_query.answer("The number of proxies is less than the number of accounts add more proxies", show_alert=True)
        return
    if not captcha:
        await callback_query.answer("The captcha service or API key is not specified install them first or activate", show_alert=True)
        return
    bot = Bot(user_id, accounts, proxies, captcha_service, captcha_api_key)
    await callback_query.answer("Account registration has started", show_alert=False)

    if user_id not in disable:
        disable[user_id] = {}
        
    disable[user_id]['register'] = True
    await callback_query.message.edit_reply_markup(reply_markup=main_menu_keyboard(user_id))
    await bot.register_process()
    disable[user_id]['register'] = False
    await callback_query.message.edit_reply_markup(reply_markup=main_menu_keyboard(user_id))
    await callback_query.message.answer('✅ Accounts registration completed')
