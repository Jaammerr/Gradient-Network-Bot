import random
import asyncio
from logger import logger
from datetime import datetime, timezone
from core.models import Account
from core.projects import Gradient
from core.utils import Mail
from core.utils.captcha import CaptchaService
from core.utils.file_manager import str_to_file
from core.utils.proxy_manager import ProxyManager
from pyuseragents import random as random_useragent
from config import threads, ref_codes, use_custom_imap, custom_imap_domain, custom_imap_folders, use_single_imap, single_imap_email, single_imap_pass

from database import update_account_points, update_account_sentry_node, update_account_verified_status, update_account_statistics


class Bot:
    def __init__(self, user_id, accounts, proxies, captcha_service: str = None, captcha_api_key: str = None):
        self.user_id = user_id
        self.ref_codes = ref_codes
        self.accounts = [Account(**account) for account in accounts]
        self.captcha_service = captcha_service
        self.captcha_api_key = captcha_api_key
        self.proxies = proxies
        self.semaphore = asyncio.Semaphore(threads)
        self.proxy_manager = ProxyManager()
        self.proxy_manager.load_proxy(proxies)
        self.should_stop = False

    async def register(self, account: Account, proxy):
            
            async with self.semaphore:

                if self.should_stop:
                    return

                try:

                    if not account.imap_password:
                        account.imap_password = account.password

                    date = datetime.now(timezone.utc)

                    ref_code = random.choice(self.ref_codes)
                    user_agent = random_useragent()
                    captcha_service = CaptchaService(self.captcha_service, self.captcha_api_key)
                    mail = Mail(account.email, account.imap_password, use_custom_imap, use_single_imap, single_imap_email, single_imap_pass, custom_imap_domain, custom_imap_folders, date)

                    client = Gradient(account, proxy, user_agent)

                    async with client:
                            
                        access_token = await client.signup()

                        if access_token:

                            await client.send_verify_email(access_token, captcha_service)
                            await asyncio.sleep(30)
                            email_code = await mail.get_msg_code_async('Here is your verification code.')
                            if email_code:
                                logger.success(f'{account} | Successfully received msg code: {email_code}')
                                await client.verify_email(access_token, email_code)
                                uid, access_token = await client.login()
                                await client.register(ref_code, access_token)
                                update_account_verified_status(True, self.user_id, account.email)
                                logger.success(f'{account} | Successfully registered and verified')

                except Exception as e:

                    error_message = str(e)

                    if "curl: (7)" in error_message or "curl: (28)" in error_message:
                        logger.error(f'{account} | Proxy failed: {proxy} | {e}')
                        await self.proxy_manager.release_proxy(proxy)
                        proxy = await self.proxy_manager.get_proxy()
                        return await self.register(account, proxy)
                    elif "curl: (35)" in error_message or "EOF" in error_message:
                        logger.error(f"{account} | SSL or Protocol Error: {proxy} | {e}")
                        await self.proxy_manager.release_proxy(proxy)
                        proxy = await self.proxy_manager.get_proxy()
                        return await self.register(account, proxy)
                    
                    str_to_file('failed.txt', account.email)
                    update_account_verified_status(False, self.user_id, account.email)
                    logger.error(f'{account} | {e}')

    async def statistics(self, account: Account, proxy: str):
            
            async with self.semaphore:

                if self.should_stop:
                    return

                try:

                    user_agent = random_useragent()

                    client = Gradient(account, proxy, user_agent)

                    async with client:

                        uid, access_token = await client.login()

                        if access_token:

                            data = await client.statistics(access_token)
                            update_account_verified_status(True, self.user_id, account.email)
                            update_account_statistics(uid, data['point']['total']/100000, data['code'], data['referredBy'], data['stats']['invitee'], data['node']['sentry'], self.user_id, account.email)
                            logger.success(f'{account} | Successfully update statistics')
                            await asyncio.sleep(5)

                except Exception as e:

                    error_message = str(e)

                    if "curl: (7)" in error_message or "curl: (28)" in error_message:
                        logger.error(f'{account} | Proxy failed: {proxy} | {e}')
                        await self.proxy_manager.release_proxy(proxy)
                        proxy = await self.proxy_manager.get_proxy()
                        return await self.statistics(account, proxy)
                    
                    elif "curl: (35)" in error_message or "EOF" in error_message:
                        logger.error(f"{account} | SSL or Protocol Error: {proxy} | {e}")
                        await self.proxy_manager.release_proxy(proxy)
                        proxy = await self.proxy_manager.get_proxy()
                        return await self.statistics(account, proxy)
                    
                    elif "user doesn't exist" in error_message or "invalid_login_credentials" in error_message or "please verify email first" in error_message:
                        update_account_verified_status(False, self.user_id, account.email)
                        str_to_file('failed.txt', account.email)
                    
                    str_to_file('failed.txt', account.email)
                    await asyncio.sleep(5)
                    logger.error(f'{account} | {e}')

    async def farm(self, account: Account, proxy: str, user_agent: str):
        
        logger.info(f"{account.email} | Start mining")
        iter_count = 0

        while not self.should_stop:

            client = None

            if account.is_verified == 0:
                logger.warning(f"{account.email} | No verified or register account")
                break
            
            async with self.semaphore:
                
                try:

                    client = Gradient(account, proxy, user_agent, self.proxy_manager)

                    async with client:

                        if iter_count % 5 == 0:
                            
                            uid, access_token = await client.login()
                            logger.success(f'{account} | Login Success')

                            if not account.client_id or not account.node_password:

                                account.client_id, account.node_password = await client.node_register(access_token)
                                
                                update_account_sentry_node(self.user_id, account.email, account.client_id, account.node_password)

                            points = await client.points(access_token)

                            if points:
                                update_account_points(self.user_id, account.email, points)
                                
                            logger.info(f"{account.email} | Info | Total Points: {points}")

                        proxy = await client.heartbeat(uid)
                    
                    iter_count+=1
                    await asyncio.sleep(150)

                except Exception as e:
                    if client:
                        await client.safe_close()

                    error_message = str(e).lower()

                    if "curl: (7)" in error_message or "curl: (28)" in error_message or "proxy" in error_message or "connect tunnel failed" in error_message:
                        logger.error(f'{account} | Proxy failed: {proxy} | {e}')
                        await self.proxy_manager.release_proxy(proxy)
                        proxy = await self.proxy_manager.get_proxy()
                    
                    elif "timed out" in error_message:
                        logger.warning(f"{account} | Timed out to connection: {proxy} | {e}")
                    
                    elif "empty document" in error_message:
                        logger.warning(f"{account} | Empty document | {e}")
                    
                    elif "user doesn't exist" in error_message or "invalid_login_credentials" in error_message or "please verify email first" in error_message:
                        account.is_verified = 0
                        update_account_verified_status(False, self.user_id, account.email)
                        str_to_file('failed.txt', account.email)
                    
                    elif "curl: (35)" in error_message or "eof occurred in violation of protocol" in error_message:
                        logger.error(f"{account} | SSL or Protocol Error: {proxy} | {e}")
                    
                    else:
                        logger.error(f'{account} | Unknown mining error: : {error_message}')
                    
                    await asyncio.sleep(10)

    async def register_process(self):

        tasks = []

        try:
            for account in self.accounts:
                proxy = await self.proxy_manager.get_proxy()
                if not self.should_stop:
                    tasks.append(
                        asyncio.create_task(
                            self.register(account, proxy)
                        )
                    )

            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f'Error register accounts process: {e}')

    async def statistics_process(self):

        tasks = []

        try:
            for account in self.accounts:
                proxy = await self.proxy_manager.get_proxy()
                if not self.should_stop:
                    tasks.append(
                        asyncio.create_task(
                            self.statistics(account, proxy)
                        )
                    )

            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f'Error statistics process: {e}')

    async def farm_process(self):

        active_tasks = {}

        try:

            for account in self.accounts:
                proxy = await self.proxy_manager.get_proxy()
                user_agent = random_useragent()
                account_key = f"{account.id}"

                if account_key not in active_tasks or active_tasks[account_key].done():
                    active_tasks[account_key] = asyncio.create_task(
                        self.farm(account, proxy, user_agent)
                    )

            active_tasks = {k: v for k, v in active_tasks.items() if not v.done()}
            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Error farm process: {e}")
        finally:
            await asyncio.gather(*active_tasks.values(), return_exceptions=True)
            logger.info("Stop farm.")

    async def stop(self):
        self.should_stop = True
