import asyncio
from typing import Awaitable, Callable, Any

import aiohttp
import json
import os
from utils import get_logger, secure

logger = get_logger("Connector")


class Connector:
    """
    Connector manages HTTP requests and a persistent, auto-reconnecting WebSocket
    connection per chat. If the WS connection drops or fails, it will retry
    every 5 seconds.
    """

    RECONNECT_DELAY = 5

    def __init__(self):
        self._secure_key = os.environ.get("API_SECURITY_KEY")
        self._base_url = os.environ.get("BACKEND_URL")
        self._session: aiohttp.ClientSession | None = None
        self._ws_tasks: dict[str, asyncio.Task] = {}
        self._websockets: dict[str, aiohttp.ClientWebSocketResponse | None] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazily create or reuse an aiohttp ClientSession."""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def connect_websocket(
            self,
            chat_id: str,
            user_id: int,
            message_handler: Callable[[dict], Awaitable[None]],
    ) -> None:
        """
        Start (or restart) a background task to maintain a WS connection
        for the given chat_id. Incoming messages will be passed to message_handler.
        """

        # If there's already a task for this chat, cancel it first
        if chat_id in self._ws_tasks:
            self._ws_tasks[chat_id].cancel()

        task = asyncio.create_task(
            self._websocket_manager(chat_id, user_id, message_handler),
            name=f"ws-manager-{chat_id}"
        )
        self._ws_tasks[chat_id] = task

    async def _websocket_manager(
            self,
            chat_id: str,
            user_id: int,
            message_handler: Callable[[dict], Awaitable[None]],
    ) -> None:
        """
        Loop forever: try to connect, listen, and on any error wait and retry.
        """
        secure_code = secure.generate_secure_token(self._secure_key, user_id)
        ws_url = (
                self._base_url
                .replace("http://", "ws://")
                .replace("https://", "wss://")
                + f"ws/chat/{chat_id}/?secure_key={secure_code}"
        )

        while True:
            try:
                session = await self._get_session()
                ws = await session.ws_connect(ws_url)
                self._websockets[chat_id] = ws
                logger.info(f"WebSocket connected for chat {chat_id} -> {ws_url}")
                await self._listen_loop(chat_id, ws, message_handler)
            except asyncio.CancelledError:
                # Task was cancelled; tear down and exit
                break
            except Exception as e:
                logger.warning(f" Websocket unexpected error for chat {chat_id}: {e!r}")
            finally:
                ws = self._websockets.pop(chat_id, None)
                if ws and not ws.closed:
                    await ws.close()
                await asyncio.sleep(self.RECONNECT_DELAY)

    async def _listen_loop(
            self,
            chat_id: str,
            ws: aiohttp.ClientWebSocketResponse,
            message_handler: Callable[[dict], Awaitable[None]],
    ) -> None:
        """Receive messages until the connection closes or errors out."""
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    logger.error(f" Invalid JSON from WS chat {chat_id}: {msg.data}")
                    continue

                if data.get("user_type") == "agent":
                    await message_handler(data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.errpr(f"WS error frame on chat {chat_id}: {ws.exception()}")
                break

    async def send_ws_message(self, chat_id: str, text: str) -> bool:
        """
        Send a text message over an existing WS connection.
        Returns True on success, False otherwise.
        """

        ws = self._websockets.get(chat_id)
        if not ws or ws.closed:
            logger.warning(f"No active WebSocket for chat {chat_id}")
            return False

        try:
            await ws.send_str(json.dumps({"text": text}))
            logger.info(f"Sent WS message to chat {chat_id}: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WS message to chat {chat_id}: {e}")
            return False

    async def post(self, data: dict, endpoint: str) -> Any | None:
        """
        Send a POST request to the given API endpoint (relative to base URL).
        Returns parsed JSON or text, or None on failure.
        """
        headers = {"X-Bot-Token": self._secure_key}
        url = self._base_url + endpoint
        try:
            session = await self._get_session()
            async with session.post(url, json=data, headers=headers) as response:
                response.raise_for_status()
                try:
                    return await response.json()
                except aiohttp.ContentTypeError:
                    return await response.text()
        except Exception as e:
            logger.error(f"POST {url} failed with error: {e!r}")

    async def create_request(self, telegram_id: int, name: str, theme: str) -> dict | None:
        """Request creation on server."""
        return await self.post(
            {"telegram_id": telegram_id, "name": name, "theme": theme},
            "api/v1/bot/create-request/",
        )

    async def send_message(self, telegram_id: int, text: str) -> dict | None:
        return await self.post(
            {"telegram_id": telegram_id, "text": text},
            "api/v1/bot/send-message/",
        )

    async def close(self):
        """Cancel all WS tasks and close HTTP session."""
        # cancel WebSocket tasks
        for task in self._ws_tasks.values():
            task.cancel()
        self._ws_tasks.clear()

        # close any open websockets
        for ws in self._websockets.values():
            await ws.close()
        self._websockets.clear()

        # close HTTP session
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("HTTP session closed.")
