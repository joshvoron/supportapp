import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from utils.project_logger import ProjectLogger

PL = ProjectLogger(
    timezone=os.environ.get("TIMEZONE", "Europe/London"), debug=os.environ.get("DEBUG", False),
    level=os.environ.get("LOGGING_LEVEL", "WARNING")
)
logger = PL.start_logging()

bot = Bot(token=os.environ.get("BOT_TOKEN"), default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))

dp = Dispatcher()
