from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.telegram_bot.keyboards import back_keyboard, cancel_keyboard
from database import add_proxies_to_user, delete_user_proxies
import re

router = Router()


class UpdateProxiesStates(StatesGroup):
    waiting_for_proxies = State()


@router.callback_query(F.data == 'data_update_proxies')
async def update_proxies_start(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message_text = (
        "<b>🌐 Update Proxies</b>\n\n"
        "⚠️ <b>Important:</b> This action will replace all existing proxies!\n\n"
        "<b>Supported Formats:</b>\n"
        "1️⃣ HTTP proxy:\n"
        "<code>http://login:password@ip:port</code>\n\n"
        "2️⃣ SOCKS5 proxy:\n"
        "<code>socks5://login:password@ip:port</code>\n\n"
        "📝 <b>Instructions:</b>\n"
        "• Put each proxy on a new line\n"
        "• Make sure proxies are active\n"
        "• Double-check all credentials\n\n"
        "You can:\n"
        "• Send proxies as a text message\n"
        "• Upload a .txt file\n\n"
        "Examples:\n"
        "<code>http://user:pass123@192.168.1.1:8080\n"
        "socks5://admin:secret@10.0.0.1:1080</code>"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=cancel_keyboard(),
        parse_mode='HTML'
    )
    await state.set_state(UpdateProxiesStates.waiting_for_proxies)


@router.message(UpdateProxiesStates.waiting_for_proxies, F.document.mime_type == 'text/plain')
async def proxies_received_file(message: types.Message, state: FSMContext):
    try:
        document = message.document
        file_id = document.file_id

        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        bytes = await message.bot.download_file(file_path)

        proxies_text = bytes.getvalue().decode('utf-8')
        await process_proxies(message, state, proxies_text)
    except Exception as e:
        error_text = (
            "❌ Failed to process file\n\n"
            "Please make sure:\n"
            "• File is in text format (.txt)\n"
            "• File uses UTF-8 encoding\n"
            "• File size is reasonable\n\n"
            "Try sending proxies as a text message instead."
        )
        await message.answer(error_text, reply_markup=back_keyboard(), parse_mode='HTML')
        await state.clear()


@router.message(UpdateProxiesStates.waiting_for_proxies)
async def proxies_received_message(message: types.Message, state: FSMContext):
    proxies_text = message.text
    await process_proxies(message, state, proxies_text)


async def process_proxies(message: types.Message, state: FSMContext, proxies_text: str):
    proxies_list = proxies_text.strip().split('\n')
    parsed_proxies = []
    invalid_proxies = []

    proxy_pattern = re.compile(r'^(http|socks5)://[\w\-.:]+@[\w\-.:]+:\d+$')

    # Count different types of proxies
    http_count = 0
    socks5_count = 0

    for i, proxy in enumerate(proxies_list, 1):
        proxy = proxy.strip()
        if not proxy:
            continue

        if not proxy_pattern.match(proxy):
            invalid_proxies.append(f"Line {i}: Invalid proxy format")
            continue

        if not (proxy.startswith('http://') or proxy.startswith('socks5://')):
            invalid_proxies.append(f"Line {i}: Must start with 'http://' or 'socks5://'")
            continue

        parsed_proxies.append(proxy)
        if proxy.startswith('http://'):
            http_count += 1
        else:
            socks5_count += 1

    if invalid_proxies:
        error_text = (
                "❌ Found invalid proxies:\n\n" +
                "\n".join(invalid_proxies) + "\n\n"
                                             "Please fix the format and try again."
        )
        await message.answer(error_text, reply_markup=back_keyboard(), parse_mode='HTML')
        await state.clear()
        return

    if not parsed_proxies:
        await message.answer(
            "❌ No valid proxies found!\n\n"
            "Please check the format and try again.",
            reply_markup=back_keyboard(),
            parse_mode='HTML'
        )
        await state.clear()
        return

    user_id = message.from_user.id
    delete_user_proxies(user_id)
    add_proxies_to_user(user_id, parsed_proxies)

    success_text = (
        "✅ Proxies Updated Successfully\n\n"
        f"📊 Statistics:\n"
        f"• Total proxies processed: {len(parsed_proxies)}\n"
        f"• HTTP proxies: {http_count}\n"
        f"• SOCKS5 proxies: {socks5_count}\n\n"
        "💡 Tips:\n"
        "• Test your proxies before using them\n"
        "• Monitor proxy performance regularly\n"
        "• Keep proxy credentials secure"
    )

    await message.answer(success_text, reply_markup=back_keyboard(), parse_mode='HTML')
    await state.clear()
