from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.telegram_bot.keyboards import back_keyboard, cancel_keyboard
from database import add_accounts_to_user

router = Router()


class AddAccountsStates(StatesGroup):
    waiting_for_accounts = State()


@router.callback_query(F.data == 'data_add_accounts')
async def add_accounts_start(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message_text = (
        "<b>📝 Add New Accounts</b>\n\n"
        "Please provide your accounts in one of these formats:\n\n"
        "1️⃣ Basic format:\n"
        "<code>email:password</code>\n\n"
        "2️⃣ Extended format (with IMAP):\n"
        "<code>email:password:imap_password</code>\n\n"
        "💡 You can:\n"
        "• Send accounts as a text message\n"
        "• Upload a .txt file\n"
        "• Put each account on a new line\n\n"
        "Example:\n"
        "<code>user@example.com:pass123\n"
        "admin@domain.com:secret:imap123</code>"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=cancel_keyboard(),
        parse_mode='HTML'
    )
    await state.set_state(AddAccountsStates.waiting_for_accounts)


@router.message(AddAccountsStates.waiting_for_accounts, F.document.mime_type == 'text/plain')
async def accounts_received_file(message: types.Message, state: FSMContext):
    document = message.document
    file_id = document.file_id

    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    bytes = await message.bot.download_file(file_path)

    accounts_text = bytes.getvalue().decode('utf-8')

    await process_accounts(message, state, accounts_text)


@router.message(AddAccountsStates.waiting_for_accounts)
async def accounts_received_message(message: types.Message, state: FSMContext):
    accounts_text = message.text
    await process_accounts(message, state, accounts_text)


async def process_accounts(message: types.Message, state: FSMContext, accounts_text: str):
    accounts_list = accounts_text.strip().split('\n')
    parsed_accounts = []

    for account in accounts_list:
        if ':' in account:
            parts = account.strip().split(':')
            email = parts[0].strip()
            password = parts[1].strip()
            imap_pass = parts[2].strip() if len(parts) > 2 else None

            parsed_accounts.append((email, password, imap_pass))
        else:
            error_text = (
                "❌ Invalid Account Format\n\n"
                "Please make sure each account follows the format:\n"
                "<code>email:password</code> or\n"
                "<code>email:password:imap_password</code>\n\n"
                "Operation has been cancelled."
            )
            await message.answer(error_text, reply_markup=back_keyboard(), parse_mode='HTML')
            await state.clear()
            return

    user_id = message.from_user.id
    add_accounts_to_user(user_id, parsed_accounts)

    success_text = (
        "✅ Accounts Added Successfully\n\n"
        f"📊 Total accounts added: {len(parsed_accounts)}\n\n"
        "You can now start using these accounts or add more."
    )

    await message.answer(success_text, reply_markup=back_keyboard())
    await state.clear()
