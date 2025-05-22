from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from texts import start_text, about_text
from keyboards.inline_kbs import start_kb, back_to_menu

start_router = Router()


@start_router.message(CommandStart())
@start_router.callback_query(F.data == 'load_start_route')
async def cmd_start(event: Message | CallbackQuery):
    if type(event) is CallbackQuery:
        await event.message.edit_text(text=start_text, reply_markup=start_kb())
    else:
        await event.answer(text=start_text, reply_markup=start_kb())


@start_router.callback_query(F.data == 'load_about_route')
async def about(call: CallbackQuery):
    await call.message.edit_text(text=about_text, reply_markup=back_to_menu())
