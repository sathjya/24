#  MIT License
#
#  Copyright (c) 2019-2020 Dan <https://github.com/delivrance>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import time
from datetime import datetime
from configparser import ConfigParser
from pyrogram import Client
from pyrogram import __version__
from pyrogram.raw.all import layer
from pyrogram.types import Message
from pyrogram import Client

assistant = Client(

    

[pyrogram]

api_id = 2171111

api_hash =  fd7acd07303760c52dcc0ed8b2f73086

bot_token = 2142246263:AAFVK-bQSh8XFwhEJZEzrXgDyoZ6QHCT-6U

)

class Assistant(Client):
    CREATOR_ID = 1089528685
    ASSISTANT_ID = 2142246263
    config = ConfigParser()
    chats = [-1001536437727 -1001263664495]

    def __init__(self):
        name = self.__class__.__name__.lower()

        self.config.read(f"{name}.ini")
        Assistant.chats = "-1001536437727"

        super().__init__(
            name,
            config_file=f"{name}.ini",
            workers=16,
            plugins=dict(
                root=f"{name}.plugins",
                exclude=["welcome"]
            ),
            sleep_threshold=180
        )

        self.admins = {
            chat: {Assistant.CREATOR_ID}
            for chat in Assistant.chats
        }

        self.uptime_reference = time.monotonic_ns()
        self.start_datetime = datetime.utcnow()

    async def start(self):
        await super().start()

        me = await self.get_me()
        print(f"Assistant for Pyrogram v{__version__} (Layer {layer}) started on @{me.username}. Hi.")

        # Fetch current admins from chats
        for chat, admins in self.admins.items():
            async for admin in self.iter_chat_members(chat, filter="administrators"):
                admins.add(admin.user.id)

    async def stop(self, *args):
        await super().stop()
        print("Pyrogram Assistant stopped. Bye.")

    def is_admin(self, message: Message) -> bool:
        user_id = message.from_user.id
        chat_id = message.chat.id

        return user_id in self.admins[chat_id]
