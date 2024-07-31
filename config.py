# -1002092954715
import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()
# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", "-1002092954715"))


PORT = os.environ.get("PORT", "8000")