from aiogram import Dispatcher

from .start import router as start_router
from .captcha_api import router as captcha_api_router
from .accounts import router as accounts_router
from .add_accounts import router as add_accounts_router
from .update_accounts import router as update_accounts_router
from .proxies import router as proxies_router
from .add_proxies import router as add_proxies_router
from .update_proxies import router as update_proxies_router
from .register_accounts import router as register_accounts_router
from .start_stop_mining import router as start_stop_mining_router
from .data import router as data_router
from .actions import router as actions_router
from .statistics import router as stats_router

def register_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(captcha_api_router)
    dp.include_router(accounts_router)
    dp.include_router(add_accounts_router)
    dp.include_router(update_accounts_router)
    dp.include_router(proxies_router)
    dp.include_router(add_proxies_router)
    dp.include_router(update_proxies_router)
    dp.include_router(register_accounts_router)
    dp.include_router(start_stop_mining_router)
    dp.include_router(data_router)
    dp.include_router(actions_router)
    dp.include_router(stats_router)
