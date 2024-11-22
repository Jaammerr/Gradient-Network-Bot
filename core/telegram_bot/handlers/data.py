from aiogram import Router, types, F
from core.telegram_bot.keyboards import data_inline_keyboard

router = Router()


@router.callback_query(F.data == "data_data")
async def data_menu(callback_query: types.CallbackQuery):
    await callback_query.answer()

    message_text = (
        "<b>⚙️ Data Management Center</b>\n\n"
        "Please select a category below 👇"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=data_inline_keyboard(),
        parse_mode="HTML"
    )
