from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
import asyncio

from utils.chat_storage import ChatStorage
from utils.connector import Connector

request_router = Router()

# Singleton instances
connector = Connector()
storage = ChatStorage()


class RequestStates(StatesGroup):
    """FSM States for the request flow."""
    theme = State()  # Waiting for the user to send the request theme
    chat = State()  # Waiting for normal chat messages to forward via WS


@request_router.callback_query(F.data == 'load_request_route')
async def create_request_step_1(
        call: CallbackQuery,
        state: FSMContext,
):
    """
    1. User clicked "Create request"
    - ask for a theme and switch to the `theme` state.
    """
    await state.set_state(RequestStates.theme)
    await call.message.answer("✏️ Please write a request theme.")


@request_router.message(RequestStates.theme)
async def create_request_step_2(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    """
    2. User sent the theme text.
    - Validate length
    - Create request on backend
    - Store chat_id
    - Open WS connection and start listening
    - Switch to `chat` state
    """
    text = msg.text or ""
    if not (3 <= len(text) <= 255):
        return await msg.answer("⚠️ Theme must be between 3 and 255 characters.")

    # 2.1 Create request on backend
    result = await connector.create_request(
        telegram_id=msg.from_user.id,
        name=msg.from_user.full_name,
        theme=text,
    )
    if not result or 'chat_id' not in result:
        return await msg.answer("❌ Failed to create request. Please try again later.")

    chat_id = result["chat_id"]
    telegram_id = result["telegram_id"]

    # 2.2 Save to JSON storage (if not exists)
    storage.add_chat(chat_id, telegram_id)

    # 2.3 Define async handler for incoming WS messages
    async def ws_message_handler(data: dict):
        text = data.get("text")
        if text:
            await bot.send_message(chat_id=msg.chat.id, text=text)

    # 2.4 Connect to WebSocket (launch listener in background)
    await connector.connect_websocket(
        chat_id=chat_id,
        user_id=msg.from_user.id,
        message_handler=ws_message_handler
    )

    await msg.answer("✅ Request created! We will answer you here shortly.")
    await state.set_state(RequestStates.chat)


@request_router.message(RequestStates.chat)
async def forward_chat_message(
        msg: Message,
):
    """
    3. User is in chat state: forward any text over WS.
    """
    text = msg.text or ""
    if not text:
        return
    chat = storage.find_chat(msg.from_user.id)
    if not chat:
        await msg.answer("⚠️ There is no active chats!")
    else:
        success = await connector.send_ws_message(chat["id"], text)
        if not success:
            await msg.answer("⚠️ Failed to send your message. Please try again.")
