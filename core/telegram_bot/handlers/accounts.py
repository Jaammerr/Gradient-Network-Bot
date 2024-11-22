from aiogram import Router, types, F
from core.telegram_bot.keyboards import data_accounts_keyboard

router = Router()


@router.callback_query(F.data == 'data_accounts')
async def accounts(callback_query: types.CallbackQuery):
    await callback_query.answer()

    message_text = (
        "<b>📱 Account Management</b>\n\n"
        "Please select an action below 👇"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=data_accounts_keyboard(),
        parse_mode='HTML'
    )
