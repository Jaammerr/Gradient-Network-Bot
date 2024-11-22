from aiogram import Router, types, F
from core.telegram_bot.keyboards import data_proxies_keyboard
from database import get_user_proxies_count

router = Router()


@router.callback_query(F.data == 'data_proxies')
async def proxies(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    proxies_count = get_user_proxies_count(user_id)

    status_emoji = "✅" if proxies_count > 0 else "⚠️"
    status_text = (
        "Active proxies available" if proxies_count > 0
        else "No proxies configured"
    )

    message_text = (
        "<b>🌐 Proxy Management</b>\n\n"
        f"Current Status:\n"
        f"• {status_emoji} {status_text}\n"
        f"• 📊 Total proxies: {proxies_count}\n\n"
        "Please select an action below 👇"
    )

    await callback_query.answer()
    await callback_query.message.edit_text(
        message_text,
        reply_markup=data_proxies_keyboard(),
        parse_mode='HTML'
    )