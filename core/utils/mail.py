import time
import asyncio
import re

from imap_tools import MailBox, AND
from logger import logger

class Mail:
    def __init__(self, email: str, imap_pass: str, custom_imap: bool, single_imap: bool, single_imap_email: str = None, single_imap_pass: str = None, imap_domain: str = None, imap_folders: dict = None, date = None):
        self.email = email
        self.single_imap = single_imap
        self.single_imap_email = single_imap_email
        self.single_imap_pass = single_imap_pass
        self.imap_pass = imap_pass
        self.date = date
        if custom_imap and imap_domain and imap_folders:
            self.imap_domain = imap_domain
            self.folders = imap_folders
        else:
            self.imap_domain, self.folders = self.parse_domain_and_folder()

    def parse_domain_and_folder(self) -> tuple:

        domain: str = self.email.split("@")[-1]
        folders = ["INBOX"]

        if any(sub in domain for sub in ['fabrikamail', 'exartimail', 'bulletsmail', 'firstmail', 'sfirstmail', 'dfirstmail', 'superocomail', 'velismail', 'reevalmail', 'veridicalmail']):
            domain = 'firstmail.ltd'
        elif any(sub in domain for sub in ['rambler', 'myrambler', 'autorambler', 'ro.ru']):
            domain = 'rambler.ru'
            folders.append("Spam")
        elif 'gmx' in domain:
            domain = 'gmx.com'
        elif 'icloud' in domain:
            domain = "mail.me.com"
            folders.extend(["Junk", "Spam"])

        return f"imap.{domain}", folders

    def get_msg_code(self, subject, delay: int = 60):

        for folder in self.folders:

            if self.single_imap:
                email = self.single_imap_email
                password = self.single_imap_pass
            else:
                email = self.email
                password = self.imap_pass
            

            with MailBox(self.imap_domain).login(email, password, initial_folder=folder) as mailbox:

                for _ in range(delay // 3):

                    try:

                        for msg in mailbox.fetch(AND(subject = subject), reverse=True):
                            
                            if self.date and msg.date < self.date:
                                continue
                            
                            if msg.html:

                                pattern = r'<div class="pDiv">(.*?)</div>'
                                matches = re.findall(pattern, msg.html, re.DOTALL)
                                code = ''.join(match.strip() for match in matches if match.strip())

                                if self.single_imap:

                                    nickname_match = re.search(r'Dear ([^,\s]+),', msg.html)

                                    if nickname_match:
                                        nickname = nickname_match.group(1)
                                        email_nickname = self.email.split('@')[0]

                                        if nickname.lower() == email_nickname.lower():
                                            if code:
                                                return code
                                            
                                else:
                                    if code:
                                        return code

                    except Exception as error:
                        logger.error(f'{self.email} | Unexpected error when getting code: {str(error)}')

        return None

    async def get_msg_code_async(self, subject, delay: int = 60):
        return await asyncio.to_thread(self.get_msg_code, subject, delay)