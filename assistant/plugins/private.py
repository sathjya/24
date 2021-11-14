from pyrogram import filters, emoji
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types.messages_and_media import message

from ..assistant import Assistant
from ..utils import docs
@Assistant.on_callback_query()
async def cb_handler(client, query):
    data = query.data
    if data == "about":
        await Message.delete

@Assistant.on_message(filters.private)
async def go(_, message: Message):
    await message.reply("**Hello**", 
        disable_web_page_preview=True,
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                f"dont Click here",
                callback_data="mm"
            ),
            
        ]])
    )
