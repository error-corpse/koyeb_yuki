from io import BytesIO
from time import sleep
from pyrogram import filters
from pyrogram.types import Message
from telegram import TelegramError, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler
import YukiBot.modules.no_sql.users_db as user_db 
from YukiBot import pbot as Yuki
from YukiBot import DEV_USERS, LOGGER as  logger, OWNER_ID, dispatcher
from YukiBot.modules.helper_funcs.chat_status import dev_plus, sudo_plus
from YukiBot.modules.no_sql.users_db import get_all_users
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    UserIsBlocked,
    PeerIdInvalid,
)
import time, asyncio, logging, datetime

USERS_GROUP = 4
CHAT_GROUP = 5
DEV_AND_MORE = DEV_USERS.append(int(OWNER_ID))


def get_user_id(username):
    # ensure valid userid
    if len(username) <= 5:
        return None

    if username.startswith("@"):
        username = username[1:]

    users = user_db.get_userid_by_name(username)

    if not users:
        return None

    if len(users) == 1:
        return users[0]["_id"]

    for user_obj in users:
        try:
            userdat = dispatcher.bot.get_chat(user_obj["_id"])
            if userdat.username == username:
                return userdat.id

        except BadRequest as excp:
            if excp.message != "⌥ ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
                logger.exception("⌥ ᴇʀʀᴏʀ ᴇxᴛʀᴀᴄᴛɪɴɢ ᴜsᴇʀ ɪᴅ")

    return None



@dev_plus
@Yuki.on_message(filters.command("bchat") & filters.user(OWNER_ID) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    all_chats = user_db.get_all_chats() or []
    await bot.send_message(
        OWNER_ID,
        f"⌥ {m.from_user.mention} ɪꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙʀᴏᴀᴅᴄᴀꜱᴛ......",
    )
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text(f"💌")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_chats = len(user_db.get_all_chats())

    for chat in all_chats:
        sts = await send_chat(chat["chat_id"], broadcast_msg)

        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            pass
        done += 1
        if not done % 20:
            await sts_msg.edit(
                f"⌥ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ ⏤͟͟͞͞★ \n\n❅ ᴛᴏᴛᴀʟ ᴄʜᴀᴛꜱ ➠  {total_chats}\n❅ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ➠ {done} / {total_chats}\n❅ sᴜᴄᴄᴇꜱꜱ ➠ {success}\n❅ ғᴀɪʟᴇᴅ ➠ {failed}"
            )
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"⌥ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ɪɴ ⏤͟͟͞͞★ {completed_in}.\n\n❅ ᴛᴏᴛᴀʟ ᴄʜᴀᴛꜱ ➠ {total_chats}\n❅ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ➠ {done} / {total_chats}\n❅ sᴜᴄᴄᴇss ➠ {success}\n❅ ғᴀɪʟᴇᴅ ➠ {failed}"
    )


async def send_chat(chat_id, message):
    try:
        await message.forward(chat_id=int(chat_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(chat_id, message)
    except InputUserDeactivated:
        logger.info(f"⌥ {chat_id} ➛ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"⌥ {chat_id} ➛ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"⌥ {chat_id} ➛ ᴜꜱᴇʀ ɪᴅ ɪɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"⌥ {chat_id} ➛ {e}")
        pass

@dev_plus
# broadcast
@Yuki.on_message(filters.command("buser") & filters.user(OWNER_ID) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    all_users = get_all_users()
    await bot.send_message(
        OWNER_ID,
        f"⌥ {m.from_user.mention} ɪꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙʀᴏᴀᴅᴄᴀꜱᴛ......",
    )
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text(f"💣")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = len(get_all_users())
    for user in all_users:
        sts = await send_msg(user["_id"], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            pass
        done += 1
        if not done % 20:
            await sts_msg.edit(
                f"⌥ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ ⏤͟͟͞͞★\n\n❅ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ ➠ {total_users}\n❅ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ➠ {done} / {total_users}\n❅ sᴜᴄᴄᴇss ➠ {success}\n❅ ғᴀɪʟᴇᴅ ➠ {failed}"
            )
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"⌥ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ⏤͟͟͞͞★\n\n❅ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ɪɴ ➠ {completed_in}\n❅ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ ➠ {total_users}\n❅ ᴄᴏᴍᴩʟᴇᴛᴇᴅ ➠ {done} / {total_users}\n❅ sᴜᴄᴄᴇss ➠ {success}\n❅ ғᴀɪʟᴇᴅ ➠ {failed}\n\n⌥ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʙʏ ➠ ๛ᴀ ᴠ ɪ s ʜ ᴀ ࿐"
    )


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"❅ {user_id} ➛ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"❅ {user_id} ➛ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"❅ {user_id} ➛ ᴜꜱᴇʀ ɪᴅ ɪɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"❅ {user_id} ➛ {e}")
        pass


# Dispatcher handlers


# Error handler
def error_callback(update: Update, context: CallbackContext):
    try:
        raise context.error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        logger.warning(f"❅ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ: {context.error}")
    except BadRequest:
        # handle malformed requests
        logger.warning(f"❅ ʙᴀᴅ ʀᴇǫᴜᴇsᴛ: {context.error}")
    except TelegramError:
        # handle all other telegram related errors
        logger.error(f"❅ ᴛᴇʟᴇɢʀᴀᴍ ᴇʀʀᴏʀ: {context.error}")
    except Exception as e:
        # handle everything else
        logger.exception(f"❅ ᴇxᴄᴇᴘᴛɪᴏɴ: {e}")


def log_user(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message

    user_db.update_user(msg.from_user.id, msg.from_user.username, chat.id, chat.title)

    if msg.reply_to_message:
        user_db.update_user(
            msg.reply_to_message.from_user.id,
            msg.reply_to_message.from_user.username,
            chat.id,
            chat.title,
        )

    if msg.forward_from:
        user_db.update_user(msg.forward_from.id, msg.forward_from.username)


@sudo_plus
def chats(update: Update, context: CallbackContext):
    all_chats = user_db.get_all_chats() or []
    chatfile = "⌥ ʟɪsᴛs ᴏғ ᴄʜᴀᴛ.\n⌥ ᴄʜᴀᴛ ɴᴀᴍᴇ | ᴄʜᴀᴛ ɪᴅ | ᴍᴇᴍʙᴇʀs ᴄᴏᴜɴᴛ\n"
    P = 1
    for chat in all_chats:
        try:
            curr_chat = context.bot.getChat(chat.chat_id)
            curr_chat.get_member(context.bot.id)
            chat_members = curr_chat.get_member_count(context.bot.id)
            chatfile += "{}. {} | {} | {}\n".format(
                P, chat.chat_name, chat.chat_id, chat_members
            )
            P = P + 1
        except:
            pass

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "groups_list.txt"
        update.effective_message.reply_document(
            document=output,
            filename="groups_list.txt",
            caption="⌥ ʜᴇʀᴇ ʙᴇ ᴛʜᴇ  ʟɪsᴛ ᴏғ ɢʀᴏᴜᴘs ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ",
        )


def chat_checker(update: Update, context: CallbackContext):
    bot = context.bot
    try:
        if update.effective_message.chat.get_member(bot.id).can_send_messages is False:
            bot.leaveChat(update.effective_message.chat.id)
    except Unauthorized:
        pass


def __user_info__(user_id):
    if user_id in [777000, 1087968824]:
        return """<b>⌥ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs ➛ </b> <code>???</code>"""
    if user_id == dispatcher.bot.id:
        return """<b>⌥ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs ➛ </b> <code>???</code>"""
    num_chats = user_db.get_user_num_chats(user_id)
    return f"""<b>⌥ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs ➛ </b> <code>{num_chats}</code>"""


def __stats__():
    return f"❅ ᴛᴏᴛᴀʟ ᴜsᴇʀs ➛ {user_db.num_users()}\n⌥ ᴀᴄʀᴏss ᴄʜᴀᴛs ➛ {user_db.num_chats()}\n"


def __migrate__(old_chat_id, new_chat_id):
    user_db.migrate_chat(old_chat_id, new_chat_id)


USER_HANDLER = MessageHandler(
    Filters.all & Filters.chat_type.groups, log_user, run_async=True
)
CHAT_CHECKER_HANDLER = MessageHandler(
    Filters.all & Filters.chat_type.groups, chat_checker, run_async=True
)
CHATLIST_HANDLER = CommandHandler("groups", chats, run_async=True)

dispatcher.add_handler(USER_HANDLER, USERS_GROUP)
dispatcher.add_handler(CHATLIST_HANDLER)
dispatcher.add_handler(CHAT_CHECKER_HANDLER, CHAT_GROUP)
dispatcher.add_error_handler(error_callback)

broadcast_handler = CommandHandler(["buser", "bchat"], broadcast_handler, filters=Filters.reply)
dispatcher.add_handler(broadcast_handler)

__mod_name__ = "ɢ-ᴄᴀsᴛ"
__handlers__ = [(USER_HANDLER, USERS_GROUP), CHATLIST_HANDLER]

__help__ = """
 ⌥ *ʙʀᴏᴀᴅᴄᴀsᴛ ➛ (ʙᴏᴛ ᴏᴡɴᴇʀ ᴏɴʟʏ)*
 ⌥ /buser *➥* ʙʀᴏᴀᴅᴄᴀsᴛs ᴛᴏᴏ ᴀʟʟ ᴜsᴇʀs.
 ⌥ /bchat *➥* ʙʀᴏᴀᴅᴄᴀsᴛs ᴛᴏᴏ ᴀʟʟ ɢʀᴏᴜᴘs.
"""