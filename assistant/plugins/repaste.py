import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

NEKO = "> nekobin.com/{}.py"
ENDPOINT = "https://nekobin.com/api/documents"
ANSWER = "**Please use Nekobin for pastes.**\n"
TIMEOUT = 3

CHAT = filters.chat("PyrogramChat")
REGEX = filters.regex(
    r"(https?://)?(www\.)?(?P<service>(p|h)asteb(\.?in|in\.com)|del\.dog|haste.thevillage.chat)/(raw/)?(?P<tag>\w+)"
    # https://regex101.com/r/cl5iGU/3
)
FILTER = REGEX & CHAT & ~filters.edited


async def get_and_post(paste_url: str):
    """Get the pasted content from a paste service and repaste it to nekobin.
    
    Returns a `str` of the key saved on nekobin or an error code as `int`.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(paste_url) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as error:
                return error.status
            payload = {"content": await response.text()}
            post = await session.post(ENDPOINT, data=payload, timeout=TIMEOUT)
            return (await post.json())["result"]["key"]


async def reply_pastes(new_pastes: str, message: Message):
    """Format a list of keys to a string and reply it."""
    new_pastes = [
        NEKO.format(paste) for paste in new_pastes if not isinstance(paste, int)
    ]
    if len(new_pastes) > 0:
        await message.reply_text(
            text=ANSWER + "\n".join(new_pastes), disable_web_page_preview=True,
        )


@Client.on_message(FILTER)
async def catch_paste(app: Client, message: Message):
    """Catch incoming pastes not on nekobin"""
    new_pastes = [
        await get_and_post(f"https://{match.group('service')}/raw/{match.group('tag')}")
        for match in message.matches
    ]
    await reply_pastes(new_pastes, message)
