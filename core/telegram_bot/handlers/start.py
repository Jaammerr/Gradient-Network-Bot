from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from database import add_user, get_user
from core.telegram_bot.keyboards import main_menu_keyboard
from datetime import datetime

router = Router()


def get_welcome_message(username: str) -> str:
    return (
        f"<b>🌟 Welcome to Gradient Bot, {username}!</b>\n\n"
        "／＞　 フ\n"
        "| 　_　 _|\n"
        "／` ミ＿xノ\n"
        "|　　　 |\n"
        "|　　　 |\n"
        "|　　　 |\n"
        "＼　　 ⌒)\n"
        "｜　　　|\n"
        "（　ヽノ\n"
        "＼　　|\n"
        "　＼　|\n"
        "　　＼|＼\n\n"
        "🎯 Ready to start? Choose any option below 👇"
    )


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Friend"
    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    user = get_user(user_id)
    if not user:
        add_user(user_id, username, created_date)

    welcome_message = get_welcome_message(username)
    await message.answer(
        welcome_message,
        reply_markup=main_menu_keyboard(user_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "start")
async def data_start(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or "Friend"
    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    user = get_user(user_id)
    if not user:
        add_user(user_id, username, created_date)

    welcome_message = get_welcome_message(username)
    await callback_query.message.edit_text(
        welcome_message,
        reply_markup=main_menu_keyboard(user_id),
        parse_mode="HTML"
    )
    await state.clear()
