from aiogram import Router, types, F
from aiogram.types import FSInputFile
from database import (
    get_user_accounts_count,
    get_user_proxies_count,
    get_total_points,
    get_user_accounts_stats,
    get_user_verified_accounts_count,
    get_user_accounts,
    get_user_proxies
)
from core.telegram_bot.keyboards import statistics_keyboard
from core.telegram_bot.shared import disable
from core.utils.file_manager import create_stats_csv
from core import Bot

router = Router()


@router.callback_query(F.data == "statistics")
async def stats(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    accounts_count = get_user_accounts_count(user_id)
    verified_accounts_count = get_user_verified_accounts_count(user_id)
    proxies_count = get_user_proxies_count(user_id)
    total_points = int(get_total_points(user_id))

    # Calculate verification percentage
    verification_rate = (verified_accounts_count / accounts_count * 100) if accounts_count > 0 else 0

    message_text = (
        "<b>📊 Statistics Dashboard</b>\n\n"
        "<b>Account Overview:</b>\n"
        f"• 👤 Total Accounts: {accounts_count}\n"
        f"• ✅ Verified Accounts: {verified_accounts_count} ({verification_rate:.1f}%)\n"
        f"• 🌐 Active Proxies: {proxies_count}\n"
        f"• 💎 Total Points: {total_points:,}\n\n"
        "Select an action below to manage your statistics 👇"
    )

    await callback_query.message.edit_text(
        message_text,
        reply_markup=statistics_keyboard(user_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "download_stats_csv")
async def download_stats(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    accounts = get_user_accounts_stats(user_id)

    headers = [
        'ID', 'UID', 'Email', 'Register', 'Points',
        'Referral Code', 'Referrer', 'Referrals', 'Nodes'
    ]

    await callback_query.answer("Preparing your statistics file...")
    create_stats_csv('statistics.csv', accounts, headers)
    csv_file = FSInputFile('statistics.csv')

    await callback_query.message.answer_document(
        document=csv_file,
        caption="📊 Here's your detailed statistics report in CSV format"
    )


@router.callback_query(F.data == "update_stats")
async def update_stats(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    accounts = get_user_accounts(user_id)
    proxies = get_user_proxies(user_id)

    # Validation checks
    if not accounts:
        await callback_query.answer(
            "⚠️ No accounts found!\n\n"
            "Please add and register accounts before updating statistics.",
            show_alert=True
        )
        return

    if not proxies:
        await callback_query.answer(
            "⚠️ No proxies configured!\n\n"
            "Please add proxies before updating statistics.",
            show_alert=True
        )
        return

    if len(proxies) < len(accounts):
        await callback_query.answer(
            "⚠️ Insufficient proxies!\n\n"
            "Please add more proxies to match the number of accounts.",
            show_alert=True
        )
        return

    bot = Bot(user_id, accounts, proxies)

    await callback_query.answer(
        "✅ Statistics update started!\n"
        "This may take a few moments...",
        show_alert=True
    )

    # Update status and keyboard
    if user_id not in disable:
        disable[user_id] = {}

    disable[user_id]['update'] = True
    await callback_query.message.edit_reply_markup(reply_markup=statistics_keyboard(user_id))

    # Process statistics update
    await bot.statistics_process()

    # Reset status and update view
    disable[user_id]['update'] = False
    await stats(callback_query)
