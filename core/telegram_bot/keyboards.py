from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.telegram_bot.shared import disable, user_tasks


def create_button(text: str, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data, url=url)


def create_keyboard(buttons: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    farm_status = user_id in user_tasks
    farm_text = "⛔️ Stop Farming" if farm_status else "🚀 Start Farming"

    register_text = "⏳ Registering..." if user_id in disable and disable[user_id].get('register') else "📝 Register"
    register_data = "disabled" if user_id in disable and disable[user_id].get('register') else "action_registration"

    return create_keyboard([
        [create_button(farm_text, "action_mining")],
        [create_button(register_text, register_data)],
        [
            create_button("💎 JamBit", url="https://t.me/JamBitPY"),
            create_button("📊 Data", "data_data")
        ],
        [
            create_button("👨‍💻 Mr. X", url="https://t.me/mrxcrypto_dev"),
            create_button("📈 Statistics", "statistics")
        ]
    ])


def data_inline_keyboard() -> InlineKeyboardMarkup:
    return create_keyboard([
        [create_button("👤 Manage Accounts", "data_accounts")],
        [create_button("🌐 Configure Proxies", "data_proxies")],
        [create_button("🔑 Setup Captcha", "data_captcha")],
        [create_button("⬅️ Back", "start")]
    ])


def data_accounts_keyboard() -> InlineKeyboardMarkup:
    return create_keyboard([
        [create_button("➕ Add Accounts", "data_add_accounts")],
        [create_button("🔄 Update Accounts", "data_update_accounts")],
        [create_button("⬅️ Back", "data_data")]
    ])


def data_proxies_keyboard() -> InlineKeyboardMarkup:
    return create_keyboard([
        [create_button("➕ Add Proxies", "data_add_proxies")],
        [create_button("🔄 Update Proxies", "data_update_proxies")],
        [create_button("⬅️ Back", "data_data")]
    ])


def captcha_services_keyboard() -> InlineKeyboardMarkup:
    services = [
        ("🤖 2Captcha", "captcha_service_2captcha"),
        ("🤖 AntiCaptcha", "captcha_service_anticaptcha"),
        ("🤖 CapMonster", "captcha_service_capmonster"),
        ("🤖 CapSolver", "captcha_service_capsolver"),
        ("🤖 CaptchaAI", "captcha_service_captchaai")
    ]

    buttons = [[create_button(text, callback_data)] for text, callback_data in services]
    buttons.append([create_button("⬅️ Back", "data_data")])

    return create_keyboard(buttons)


def data_captcha_service_keyboard(status: bool) -> InlineKeyboardMarkup:
    buttons = []

    if status is None:
        buttons.append([create_button("🔑 Add API Key", "data_add_captcha_api_key")])
    else:
        buttons.append([create_button("🔄 Update API Key", "data_update_captcha_api_key")])

        status_text = '⭕️ Deactivate' if status else '✅ Activate'
        status_data = 'data_captcha_service_deactivate' if status else 'data_captcha_service_activate'
        buttons.append([create_button(status_text, status_data)])

    buttons.append([create_button("⬅️ Back", "data_captcha")])
    return create_keyboard(buttons)


def statistics_keyboard(user_id: int) -> InlineKeyboardMarkup:
    update_text = "⏳ Updating..." if user_id in disable and disable[user_id].get('update') else "🔄 Update"
    update_data = "disabled" if user_id in disable and disable[user_id].get('update') else "update_stats"

    return create_keyboard([
        [create_button("📥 Export", "download_stats_csv")],
        [create_button(update_text, update_data)],
        [create_button("⬅️ Back", "start")]
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return create_keyboard([[create_button("❌ Cancel", "start")]])


def back_keyboard() -> InlineKeyboardMarkup:
    return create_keyboard([[create_button("⬅️ Back to Main Menu", "start")]])
