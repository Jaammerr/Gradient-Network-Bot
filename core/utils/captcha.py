import asyncio
import captchatools
from logger import logger

CAPTCHA_PARAMS = {
    'captcha_type': 'v2',
    'invisible_captcha': False,
    'sitekey': '6Lfe5TAqAAAAAI3mJZFYU17Rzjh9DB5KDRReuqYV',
    'captcha_url': 'app.gradient.network'
}


class CaptchaService:
    def __init__(self, service, api_key):
        self.api_key = api_key
        self.service = service

    def get_captcha_token(self):
        captcha_config = self.parse_captcha_type()
        solver = captchatools.new_harvester(**captcha_config, **CAPTCHA_PARAMS)
        return solver.get_token()

    def parse_captcha_type(self):
        return {'solving_site': self.service, 'api_key': self.api_key}

    async def get_captcha_token_async(self):
        logger.info('Sending captcha')
        return await asyncio.to_thread(self.get_captcha_token)