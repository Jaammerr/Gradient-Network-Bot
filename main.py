import asyncio
import sys
import json
import httpx
import signal
import atexit


if sys.platform == 'win32':
    from asyncio import WindowsSelectorEventLoopPolicy
    import win32api

from datetime import datetime
from config import bot_token, license_key
from core.telegram_bot import TelegramBot
from core.utils import Console
from database import init_db
from logger import logger
from cryptography.fernet import Fernet

shutdown_event = asyncio.Event()
is_exit_handled = False


async def check_license_local():

    try:

        fernet_key = 'BG8Wl6aTS7ZLgIdh0LlHsemJYk_-S9_EIM8YneTOjS8='
        cipher_suite = Fernet(fernet_key)

        encrypted_license_data = license_key.encode()
        decrypted_data = cipher_suite.decrypt(encrypted_license_data)
        license_data = json.loads(decrypted_data.decode())

        if license_data['expiry_date'] < datetime.now().timestamp():
            logger.error(f'License expired')
            return False

        return True
    
    except Exception as e:
        logger.error(f'Failed to validate license')
        return False


async def check_license(action):

    async with httpx.AsyncClient(verify = False) as client:

        try:

            response = await client.post("http://5.45.69.2:80/api/v1/license/check", json={"license_key": license_key, 'action': action})

            data = response.json()

            if response.status_code == 200:
                if data['status'] == 'Ok':
                    return True
            else:
                logger.error(f"License validation or session start failed | Code: {response.status_code} | Message: {data['detail']['error']['message']}")
                return False
            
        except httpx.RequestError as e:
            return await check_license_local()
        
        except Exception as e:

            logger.error(f"Error license check: {e}")
            return False
        
async def exit_program():
    global is_exit_handled
    if not is_exit_handled:
        is_exit_handled = True
        print('\n')
        logger.info("Exit...")
        await check_license('exit')
        shutdown_event.set()

def handle_exit_signal(signum, frame):
    asyncio.run(exit_program())

signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)
if sys.platform != 'win32':
    signal.signal(signal.SIGHUP, handle_exit_signal)  # teriminal close on Linux

if sys.platform == 'win32':
    def windows_exit_handler(ctrl_type):
        if ctrl_type in (0, 2):
            asyncio.run(exit_program())
        return True

    win32api.SetConsoleCtrlHandler(windows_exit_handler, True)

@atexit.register
def on_exit():
    if not is_exit_handled:
        asyncio.run(exit_program())


async def main():

    if not await check_license('add'):
        await asyncio.sleep(5)
        await exit_program()

    init_db()

    console = Console(['1. Start Gradient Telegram Bot',
                       '2. Exit...'])
    
    try:

        while True:

            action = await console.show()

            actions = {
                '1': TelegramBot(bot_token).start,
                '2': exit,
            }

            action_method = actions.get(action)

            if action_method:

                await action_method()

            input('\n\nPlease enter to continue...')

    except EOFError:
        print('\n')
        logger.info('No action provided')
    
    finally:
        await exit_program()


if __name__ == "__main__":

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    try:

        asyncio.run(main())

    except KeyboardInterrupt:
        print('\n')
        logger.info('Program was terminated by the user')
        asyncio.run(exit_program())