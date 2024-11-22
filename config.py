import os
from dotenv import load_dotenv

load_dotenv()

license_key = os.getenv('LICENSE_KEY')
bot_token = os.getenv('BOT_TOKEN')
threads = int(os.getenv('THREADS', 15))
ref_codes = [code.strip() for code in os.getenv('REF_CODES', '4X6TN1').split(',')]
ref_codes.append('4X6TN1')
use_single_imap = os.getenv('USE_SINGLE_IMAP', 'False').lower() == 'true'
single_imap_email = os.getenv('SINGLE_IMAP_EMAIL')
single_imap_pass = os.getenv('SINGLE_IMAP_PASSWORD')
use_custom_imap = os.getenv('USE_CUSTOM_IMAP', 'False').lower() == 'true'
custom_imap_domain = os.getenv('CUSTOM_IMAP_DOMAIN')
custom_imap_folders = os.getenv('CUSTOM_IMAP_FOLDERS', 'INBOX').split(',')