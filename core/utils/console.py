import os
from art import tprint

class Console:
    def __init__(self, actions: list = None):
        self.actions = actions

    async def show(self, actions: list = None):

            actions = actions or self.actions

            if actions:
                os.system('cls' if os.name == 'nt' else 'clear')

                tprint('Gradient')

                print("\033[94m> v. 1.1.3\n\n"
                    "\033[94m> https://t.me/mrxcrypto_dev\n"
                    "\033[94m> https://github.com/mrxdegen\n"
                    "\033[94m> https://t.me/JamBitPY\n"
                    "\033[94m> https://github.com/Jaammerr\n\n"
                    "\033[97mActions:\n\n"
                    "\033[32m[Telegram Bot]\n"
                    "\033[97m{}".format(
                        "\n".join(self.actions)
                ))

                action = input(f"\nSelect an action: ")
                print(f"\033[92mYou selected: {action}\033[0m")

                return action