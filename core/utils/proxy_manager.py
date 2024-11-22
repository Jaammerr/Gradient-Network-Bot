import asyncio
from collections import deque
from better_proxy import Proxy
from core.utils.file_manager import file_to_list


class ProxyManager:
    def __init__(self):
        self.proxies = deque()
        self.lock = asyncio.Lock()

    def load_proxy(self, proxies):
        self.proxies = deque([Proxy.from_str(proxy).as_url for proxy in proxies])

    async def get_proxy(self):
        """Return the first available proxy."""
        async with self.lock:
            if self.proxies:
                proxy = self.proxies.popleft()
                return proxy
            return None

    async def release_proxy(self, proxy: str):
        """Release the proxy back into the available pool."""
        async with self.lock:
            self.proxies.append(proxy)