from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.telegram_bot.keyboards import back_keyboard, cancel_keyboard
from database import add_accounts_to_user, delete_user_accounts
import re

router = Router()


class UpdateAccountsStates(StatesGroup):
    waiting_for_accounts = State()


@router.callback_query(F.data == 'data_update_accounts')
async def update_accounts_start(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message_text = (
        "<b>🔄 Update Accounts</b>\n\n"
        "⚠️ <b>Important:</b> This action will replace all existing accounts!\n\n"
        "<b>Supported Formats:</b>\n"
        "1️⃣ Basic format:\n"
        "<code>email:password</code>\n\n"
        "2️⃣ Extended format (with IMAP):\n"
        "<code>email:password:imap_password</code>\n\n"
        "📝 <b>Instructions:</b>\n"
        "• Put each account on a new line\n"
        "• Make sure there are no empty lines\n"
        "• Double-check all credentials\n\n"
        "You can:\n"
        "• Send accounts as a text message\n"
        "• Upload a .txt file\n\n"
        "Example:\n"
        "<code>user@mail.com:pass123\n"
        "admin@mail.com:secret:imap456</code>"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=cancel_keyboard(),
        parse_mode='HTML'
    )
    await state.set_state(UpdateAccountsStates.waiting_for_accounts)


@router.message(UpdateAccountsStates.waiting_for_accounts, F.document.mime_type == 'text/plain')
async def accounts_received_file(message: types.Message, state: FSMContext):
    try:
        document = message.document
        file_id = document.file_id

        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        bytes = await message.bot.download_file(file_path)

        accounts_text = bytes.getvalue().decode('utf-8')
        await process_accounts(message, state, accounts_text)
    except Exception as e:
        error_text = (
            "❌ Failed to process file\n\n"
            "Please make sure:\n"
            "• File is in text format (.txt)\n"
            "• File uses UTF-8 encoding\n"
            "• File size is reasonable\n\n"
            "Try sending accounts as a text message instead."
        )
        await message.answer(error_text, reply_markup=back_keyboard(), parse_mode='HTML')
        await state.clear()


@router.message(UpdateAccountsStates.waiting_for_accounts)
async def accounts_received_message(message: types.Message, state: FSMContext):
    accounts_text = message.text
    await process_accounts(message, state, accounts_text)


async def process_accounts(message: types.Message, state: FSMContext, accounts_text: str):
    accounts_list = accounts_text.strip().split('\n')
    parsed_accounts = []
    invalid_accounts = []

    for i, account in enumerate(accounts_list, 1):
        if ':' in account:
            parts = account.strip().split(':')
            if 2 <= len(parts) <= 3:
                email = parts[0].strip()
                password = parts[1].strip()
                imap_pass = parts[2].strip() if len(parts) > 2 else None

                # Basic email validation
                if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    parsed_accounts.append((email, password, imap_pass))
                else:
                    invalid_accounts.append(f"Line {i}: Invalid email format")
            else:
                invalid_accounts.append(f"Line {i}: Wrong number of credentials")
        else:
            invalid_accounts.append(f"Line {i}: Missing separator ':'")

    if invalid_accounts:
        error_text = (
                "❌ Found invalid accounts:\n\n" +
                "\n".join(invalid_accounts) + "\n\n"
                                              "Please fix the format and try again."
        )
        await message.answer(error_text, reply_markup=back_keyboard(), parse_mode='HTML')
        await state.clear()
        return

    if not parsed_accounts:
        await message.answer(
            "❌ No valid accounts found!\n\n"
            "Please check the format and try again.",
            reply_markup=back_keyboard(),
            parse_mode='HTML'
        )
        await state.clear()
        return

    user_id = message.from_user.id
    delete_user_accounts(user_id)
    add_accounts_to_user(user_id, parsed_accounts)

    success_text = (
        "✅ Accounts Updated Successfully\n\n"
        f"📊 Statistics:\n"
        f"• Total accounts processed: {len(parsed_accounts)}\n"
        f"• Basic accounts: {sum(1 for _, _, imap in parsed_accounts if not imap)}\n"
        f"• IMAP-enabled accounts: {sum(1 for _, _, imap in parsed_accounts if imap)}\n\n"
        "All previous accounts have been replaced with the new ones."
    )

    await message.answer(success_text, reply_markup=back_keyboard(), parse_mode='HTML')
    await state.clear()
