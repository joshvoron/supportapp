import asyncio
import handlers as handlers
from bot_create import bot, dp
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands():
    commands = [BotCommand(command='start', description="Let's begin!"),
                BotCommand(command='about',
                           description="Information about this bot"),
                BotCommand(command='support', description="Try SupportApp")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main():
    dp.include_routers(handlers.start_router, handlers.request_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands()
    await dp.start_polling(bot)
    await set_commands()


if __name__ == "__main__":
    asyncio.run(main())
