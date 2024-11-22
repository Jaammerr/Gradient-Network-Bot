from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.telegram_bot.keyboards import back_keyboard, cancel_keyboard
from database import add_proxies_to_user

router = Router()


class AddProxiesStates(StatesGroup):
    waiting_for_proxies = State()


@router.callback_query(F.data == 'data_add_proxies')
async def add_proxies_start(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message_text = (
        "<b>🌐 Add New Proxies</b>\n\n"
        "Please provide your proxies in one of these formats:\n\n"
        "1️⃣ HTTP proxy:\n"
        "<code>http://login:password@ip:port</code>\n\n"
        "2️⃣ SOCKS5 proxy:\n"
        "<code>socks5://login:password@ip:port</code>\n\n"
        "💡 You can:\n"
        "• Send proxies as a text message\n"
        "• Upload a .txt file\n"
        "• Put each proxy on a new line\n\n"
        "Examples:\n"
        "<code>http://user:pass123@192.168.1.1:8080\n"
        "socks5://admin:secret@10.0.0.1:1080</code>\n\n"
        "⚠️ Make sure your proxies are active and properly formatted"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=cancel_keyboard(),
        parse_mode='HTML'
    )
    await state.set_state(AddProxiesStates.waiting_for_proxies)


@router.message(AddProxiesStates.waiting_for_proxies, F.document.mime_type == 'text/plain')
async def proxies_received_file(message: types.Message, state: FSMContext):
    document = message.document
    file_id = document.file_id

    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    bytes = await message.bot.download_file(file_path)

    proxies_text = bytes.getvalue().decode('utf-8')

    await process_proxies(message, state, proxies_text)


@router.message(AddProxiesStates.waiting_for_proxies)
async def proxies_received_message(message: types.Message, state: FSMContext):
    proxies_text = message.text
    await process_proxies(message, state, proxies_text)


async def process_proxies(message: types.Message, state: FSMContext, proxies_text: str):
    proxies_list = proxies_text.strip().split('\n')
    parsed_proxies = []

    for proxy in proxies_list:
        proxy = proxy.strip()
        if not (proxy.startswith('http://') or proxy.startswith('socks5://')):
            error_text = (
                "❌ Invalid Proxy Format\n\n"
                "Each proxy must start with:\n"
                "• <code>http://</code> for HTTP proxies\n"
                "• <code>socks5://</code> for SOCKS5 proxies\n\n"
                "Please check your proxy format and try again."
            )
            await message.answer(error_text, reply_markup=back_keyboard(), parse_mode='HTML')
            await state.clear()
            return
        parsed_proxies.append(proxy)

    user_id = message.from_user.id
    add_proxies_to_user(user_id, parsed_proxies)

    success_text = (
        "✅ Proxies Added Successfully\n\n"
        f"📊 Total proxies added: {len(parsed_proxies)}\n"
        "Your proxies are now ready to use\n\n"
        "💡 Tip: Make sure to test your proxies before using them in production"
    )

    await message.answer(success_text, reply_markup=back_keyboard())
    await state.clear()
