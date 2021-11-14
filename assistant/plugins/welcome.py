from pyrogram import filters, emoji
from pyrogram.methods import Filters
from pyrogram.types import Message

from ..assistant import Assistant


@Assistant.on_message(Filters.chat(Assistant.chats) & Filters.new_chat_members)
async def welcome(_, message: Message):
    new_members = [f"{u.mention}" for u in message.new_chat_members]
    text = "Welcome to 24's group chat {', '.join(new_members)}!"

    await message.reply_text(text, disable_web_page_preview=True)
