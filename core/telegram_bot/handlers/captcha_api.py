import captchatools
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.telegram_bot.keyboards import captcha_services_keyboard, data_captcha_service_keyboard, back_keyboard, cancel_keyboard
from database import (update_user_captcha_key, get_user_captcha_service_and_key_stats,
                      get_user_captcha_service_and_key, update_user_captcha_status, add_captcha_to_user)
from aiogram.types import CallbackQuery

router = Router()


class CaptchaAPIStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_api_key = State()


captcha_services = {
    'anticaptcha': 'AntiCaptcha',
    '2captcha': '2Captcha',
    'capmonster': 'CapMonster',
    'capsolver': 'CapSolver',
    'captchaai': 'CaptchaAI'
}


def mask_key(api_key):
    if len(api_key) > 9:
        return f"{api_key[:5]}...{api_key[-4:]}"
    return api_key


@router.callback_query(F.data == 'data_captcha')
async def captcha_api_start(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    user_captcha_services = get_user_captcha_service_and_key_stats(user_id)
    messages = []

    header = (
        "<b>🔐 Captcha Services Dashboard</b>\n\n"
        "Current Services Status 👇"
    )

    for service in captcha_services:
        service_data = next((item for item in user_captcha_services if item['service'] == service), None)
        service_name = captcha_services[service]

        if service_data:
            api_key, status = service_data['api_key'], service_data['status']
            status_text = "✅ Active" if status else "⚫️ Inactive"
            masked_key = mask_key(api_key)
            solver = captchatools.new_harvester(**{'solving_site': service, 'api_key': api_key})
            balance = f'\n💰 Balance: ${solver.get_balance():.3f}'
        else:
            balance = ''
            status_text = "⚫️ Not configured"
            masked_key = "❌ No API key"

        messages.append(
            f"<b>🔹 {service_name}</b>\n"
            f"Status: {status_text}\n"
            f"API Key: {masked_key}{balance}"
        )

    message = "\n\n".join([header] + messages + ["\nSelect a service to configure 👇"])
    await callback_query.message.edit_text(message, reply_markup=captcha_services_keyboard(), parse_mode="HTML")
    await state.set_state(CaptchaAPIStates.waiting_for_service)


@router.callback_query(CaptchaAPIStates.waiting_for_service, F.data.func(lambda data: data.startswith('captcha_service_')))
async def captcha_service_chosen(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    service = data.get('captcha_service')

    if not service:
        service = callback_query.data.split('_', 2)[2]
        await state.update_data(captcha_service=service)

    user_captcha_service = get_user_captcha_service_and_key(user_id, service)
    service_name = captcha_services[service]

    if user_captcha_service:
        api_key, status = user_captcha_service['api_key'], user_captcha_service['status']
        solver = captchatools.new_harvester(**{'solving_site': service, 'api_key': api_key})
        balance = f'\n💰 Balance: ${solver.get_balance():.3f}'
        status_text = "✅ Active" if status else "⚫️ Inactive"
        masked_key = mask_key(api_key)
    else:
        status = None
        balance = ''
        status_text = "⚫️ Not configured"
        masked_key = "❌ No API key"

    message = (
        f"<b>⚙️ {service_name} Configuration</b>\n\n"
        f"<b>Current Status:</b>\n"
        f"• Operation Status: {status_text}\n"
        f"• API Key: {masked_key}{balance}\n\n"
        "Choose an action below 👇"
    )

    await callback_query.message.edit_text(message, reply_markup=data_captcha_service_keyboard(status), parse_mode="HTML")


@router.callback_query(F.data.in_(['data_update_captcha_api_key', 'data_add_captcha_api_key']))
async def captcha_service_update_or_add_api_key(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_name = captcha_services[data.get('captcha_service')]

    message = (
        f"<b>🔑 Enter {service_name} API Key</b>\n\n"
        f"Please provide your {service_name} API key:\n\n"
        "💡 Tips:\n"
        "• Make sure the key is active\n"
        "• Check for extra spaces\n"
        "• Key will be validated automatically\n\n"
        "Send your API key 👇"
    )

    await callback_query.message.edit_text(message, reply_markup=cancel_keyboard(), parse_mode="HTML")
    await state.set_state(CaptchaAPIStates.waiting_for_api_key)


@router.callback_query(F.data.in_(['data_captcha_service_activate', 'data_captcha_service_deactivate']))
async def captcha_service_update_status(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    service = data.get('captcha_service')
    service_name = captcha_services[service]
    show_alert = False

    if callback_query.data == 'data_captcha_service_activate':
        user_active_captcha_service = get_user_captcha_service_and_key(user_id)
        if user_active_captcha_service:
            message = '⚠️ Action failed: Another service is already active'
            show_alert = True
        else:
            update_user_captcha_status(user_id, True, service)
            message = '✅ Service successfully activated'
    else:
        update_user_captcha_status(user_id, False, service)
        message = '⚫️ Service successfully deactivated'

    await callback_query.answer(f"{service_name}: {message}", show_alert=show_alert)
    await captcha_service_chosen(callback_query, state)


@router.message(CaptchaAPIStates.waiting_for_api_key)
async def captcha_api_key_received(message: types.Message, state: FSMContext):
    data = await state.get_data()
    service = data.get('captcha_service')
    service_name = captcha_services[service]
    api_key = message.text.strip()
    user_id = message.from_user.id

    try:
        solver = captchatools.new_harvester(**{'solving_site': service, 'api_key': api_key})
        balance = solver.get_balance()
        user_captcha_service = get_user_captcha_service_and_key(user_id, service)
        user_active_captcha_service = get_user_captcha_service_and_key(user_id)

        if user_captcha_service:
            update_user_captcha_key(user_id, api_key, service)
        else:
            status = not bool(user_active_captcha_service)
            add_captcha_to_user(user_id, service, api_key, status)

        masked_key = mask_key(api_key)
        success_message = (
            f"✅ {service_name} API Key Added Successfully\n\n"
            f"<b>Configuration Details:</b>\n"
            f"• API Key: {masked_key}\n"
            f"• Current Balance: ${balance:.3f}\n"
            f"• Status: {'✅ Active' if not user_active_captcha_service else '⚫️ Ready to activate'}\n\n"
            f"Your {service_name} service is now configured and ready to use!"
        )
        await message.answer(success_message, reply_markup=back_keyboard(), parse_mode="HTML")
    except Exception as e:
        error_message = (
            f"❌ Invalid API Key\n\n"
            f"Could not validate the {service_name} API key.\n\n"
            "Common issues:\n"
            "• Incorrect API key format\n"
            "• Expired or inactive key\n"
            "• Connection problems\n\n"
            "Please check your key and try again."
        )
        await message.answer(error_message, reply_markup=back_keyboard(), parse_mode="HTML")

    await state.clear()
