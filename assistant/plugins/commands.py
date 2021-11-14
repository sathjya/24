import asyncio
import time
from functools import partial, wraps

import aiohttp
from num2words import num2words
from pyrogram import filters, emoji
from pyrogram.types import CallbackQuery, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..assistant import Assistant
from ..utils import docs

command = partial(filters.command, prefixes=list("#!"))


async def reply_and_delete(message: Message, text: str):
    await asyncio.gather(
        message.delete(),
        message.reply(
            text,
            quote=False,
            reply_to_message_id=getattr(
                message.reply_to_message,
                "message_id", None
            ),
            disable_web_page_preview=True
        )
    )


def admins_only(func):
    @wraps(func)
    async def decorator(bot: Assistant, message: Message):
        if bot.is_admin(message):
            await func(bot, message)

        await message.delete()

    decorator.admin = True

    return decorator


################################

PING_TTL = 5


@Assistant.on_message(command("ping"))
async def ping(_, message: Message):
    """Ping the assistant"""
    start = time.time()
    reply = await message.reply_text("...")
    delta_ping = time.time() - start
    await reply.edit_text(f"**Pong!** `{delta_ping * 1000:.3f} ms`")


################################


SCHEMA = "https"
BASE = "nekobin.com"
ENDPOINT = f"{SCHEMA}://{BASE}/api/documents"
ANSWER = "**Long message from** {}\n{}"
TIMEOUT = 3
MESSAGE_ID_DIFF = 100


@Assistant.on_message(command("neko"))
@admins_only
async def neko(_, message: Message):
    """Paste very long code"""
    reply = message.reply_to_message

    if not reply:
        return

    # Ignore messages that are too old
    if message.message_id - reply.message_id > MESSAGE_ID_DIFF:
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(
            ENDPOINT,
            json={"content": reply.text},
            timeout=TIMEOUT
        ) as response:
            key = (await response.json())["result"]["key"]

    await reply_and_delete(reply, ANSWER.format(reply.from_user.mention, f"{BASE}/{key}.py"))


################################################################################################
################################
################################
################################
################################

################################


################################

################################

################################


################################



################################


################################

MESSAGE_DATE_DIFF = 43200  # 12h


@Assistant.on_message(command("delete"))
@admins_only
async def delete(bot: Assistant, message: Message):
    """Delete messages"""
    reply = message.reply_to_message

    if not reply:
        return

    # Don't delete admins messages
    if bot.is_admin(reply):
        m = await message.reply("Sorry, I don't delete administrators' messages.")
        await asyncio.sleep(5)
        await m.delete()
        return

    # Don't delete messages that are too old
    if message.date - reply.date > MESSAGE_DATE_DIFF:
        m = await message.reply("Sorry, I don't delete messages that are too old.")
        await asyncio.sleep(5)
        await m.delete()
        return

    cmd = message.command

    # No args, delete the mentioned message alone
    if len(cmd) == 1:
        await reply.delete()
        return

    # Delete the last N messages of the mentioned user, up to 200

    arg = int(cmd[1])

    # Min 1 max 200
    arg = max(arg, 1)
    arg = min(arg, 200)

    last_200 = range(reply.message_id, reply.message_id - 200, -1)

    message_ids = [
        m.message_id for m in filter(
            lambda m: m.from_user and m.from_user.id == reply.from_user.id,
            await bot.get_messages(message.chat.id, last_200, replies=0)
        )
    ]

    await bot.delete_messages(message.chat.id, message_ids[:arg])


################################

@Assistant.on_message(command("ban"))
@admins_only
async def ban(bot: Assistant, message: Message):
    """Ban a user in chat"""
    reply = message.reply_to_message

    if not reply:
        return

    # Don't ban admins
    if bot.is_admin(reply):
        m = await message.reply("Sorry, I don't ban administrators")
        await asyncio.sleep(5)
        await m.delete()
        return

    await bot.restrict_chat_member(message.chat.id, reply.from_user.id, ChatPermissions())

    await message.reply(
        f"__Banned {reply.from_user.mention} indefinitely__",
        quote=False,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Give grace", f"unban.{reply.from_user.id}")
        ]])
    )


################################

@Assistant.on_message(command("kick"))
@admins_only
async def kick(bot: Assistant, message: Message):
    """Kick (they can rejoin)"""
    reply = message.reply_to_message

    if not reply:
        return

    # Don't kick admins
    if bot.is_admin(reply):
        m = await message.reply("Sorry, I don't kick administrators")
        await asyncio.sleep(5)
        await m.delete()
        return

    # Default ban until_time 60 seconds later as failsafe in case unban doesn't work
    # (can happen in case the server processes unban before ban and thus ignoring unban)
    await bot.kick_chat_member(message.chat.id, reply.from_user.id, int(time.time()) + 60)

    await message.reply(
        f"__Kicked {reply.from_user.mention}. They can rejoin__",
        quote=False
    )

    await asyncio.sleep(5)  # Sleep to allow the server some time to process the kick
    await bot.unban_chat_member(message.chat.id, reply.from_user.id)


################################

@Assistant.on_message(command("nab"))
@admins_only
async def nab(bot: Assistant, message: Message):
    reply = message.reply_to_message

    if not reply:
        return

    target = reply.from_user

    if target.id in [bot.CREATOR_ID, bot.ASSISTANT_ID]:
        target = message.from_user

    await message.reply(
        f"__Banned {target.mention} indefinitely__",
        quote=False
    )


################################


################################

################################

# Pattern: https://regex101.com/r/6xdeRf/3
@Assistant.on_callback_query(filters.regex(r"^(?P<action>remove|unban)\.(?P<uid>\d+)"))
async def cb_query(bot: Assistant, query: CallbackQuery):
    match = query.matches[0]
    action = match.group("action")
    user_id = int(match.group("uid"))
    text = query.message.text

    if action == "unban":
        if query.from_user.id != Assistant.CREATOR_ID:
            await query.answer("Only me can pardon banned users", show_alert=True)
            return

        await bot.restrict_chat_member(
            query.message.chat.id,
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_stickers=True,
                can_send_animations=True,
                can_send_games=True,
                can_use_inline_bots=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )

        await query.edit_message_text(f"~~{text.markdown}~~\n\nPardoned")

    if action == "remove":
        # Dummy Message object to check if the user is admin.
        # Re: https://t.me/pyrogramlounge/324583
        dummy = Message(
            message_id=0,
            from_user=query.from_user,
            chat=query.message.chat
        )
        if query.from_user.id == user_id or bot.is_admin(dummy):
            await query.answer()
            await query.message.delete()
        else:
            await query.answer("Only Admins can remove the help messages.")


################################

@Assistant.on_message(command("up"))
async def up(bot: Assistant, message: Message):
    """Show Assistant's uptime"""
    uptime = time.monotonic_ns() - bot.uptime_reference

    us, ns = divmod(uptime, 1000)
    ms, us = divmod(us, 1000)
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    try:
        arg = message.command[1]
    except IndexError:
        await reply_and_delete(message, f"**Uptime**: `{d}d {h}h {m}m {s}s`")
    else:
        if arg == "-v":
            await reply_and_delete(
                message,
                f"**Uptime**: `{d}d {h}h {m}m {s}s {ms}ms {us}μs {ns}ns`\n"
                f"**Since**: `{bot.start_datetime} UTC`"
            )
        elif arg == "-p":
            await reply_and_delete(
                message,
                f"**Uptime**: "
                f"`{num2words(d)} days, {num2words(h)} hours, {num2words(m)} minutes, "
                f"{num2words(s)} seconds, {num2words(ms)} milliseconds, "
                f"{num2words(us)} microseconds, {num2words(ns)} nanoseconds`\n"
                f""
                f"**Since**: `year {num2words(bot.start_datetime.year)}, "
                f"month {bot.start_datetime.strftime('%B').lower()}, day {num2words(bot.start_datetime.day)}, "
                f"hour {num2words(bot.start_datetime.hour)}, minute {num2words(bot.start_datetime.minute)}, "
                f"second {num2words(bot.start_datetime.second)}, "
                f"microsecond {num2words(bot.start_datetime.microsecond)}, Coordinated Universal Time`"
            )
        else:
            await message.delete()


################################

# noinspection PyShadowingBuiltins
@Assistant.on_message(command("help"))
async def help(bot: Assistant, message: Message):
    """Show this message"""
    await asyncio.gather(
        message.delete(),
        message.reply(
            HELP,
            quote=False,
            reply_to_message_id=getattr(
                message.reply_to_message,
                "message_id", None
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Remove Help", f"remove.{message.from_user.id}")
            ]]),
        )
    )


################################

nl = "\n"

HELP = f"""
**List of available commands**

{nl.join(
    f"• #{fn[0]}{'`*`' if hasattr(fn[1], 'admin') else ''} - {fn[1].__doc__}"
    for fn in locals().items()
    if hasattr(fn[1], "handler")
    and fn[0] not in ["cb_query", "repost_rules", "nab"])}

`*` Administrators only
"""
