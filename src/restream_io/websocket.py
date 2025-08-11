"""WebSocket client for real-time monitoring of Restream.io APIs."""

import asyncio
import json
import logging
import signal
import sys
from typing import AsyncGenerator, Callable, Optional

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from .auth import get_access_token
from .errors import AuthenticationError

logger = logging.getLogger(__name__)


class WebSocketClient:
    """Base WebSocket client for real-time monitoring."""

    def __init__(self, uri: str, duration: Optional[int] = None):
        """Initialize WebSocket client.

        Args:
            uri: WebSocket URI to connect to
            duration: Optional duration in seconds to monitor (None for indefinite)
        """
        self.uri = uri
        self.duration = duration
        self.websocket = None
        self._running = False
        self._stop_event = asyncio.Event()

    async def connect(self) -> None:
        """Establish WebSocket connection with authentication."""
        try:
            access_token = get_access_token()
            if not access_token:
                raise AuthenticationError("No valid access token available")

            # Add access token as query parameter as per official docs
            uri_with_token = f"{self.uri}?accessToken={access_token}"

            self.websocket = await websockets.connect(
                uri_with_token,
                ping_interval=30,
                ping_timeout=10,
            )
            logger.info(f"Connected to {self.uri}")

        except Exception as e:
            logger.error(f"Failed to connect to {self.uri}: {e}")
            raise

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("WebSocket connection closed")

    async def listen(self, message_handler: Callable[[dict], None]) -> None:
        """Listen for messages and handle them.

        Args:
            message_handler: Callback function to handle received messages
        """
        self._running = True

        # Set up signal handlers for graceful shutdown
        if sys.platform != "win32":
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, self._signal_handler)

        try:
            # Set up duration-based timeout if specified
            if self.duration:
                asyncio.create_task(self._duration_timeout())

            await self.connect()

            async for message in self._message_stream():
                if not self._running:
                    break

                try:
                    data = json.loads(message)
                    message_handler(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse message as JSON: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Error during WebSocket listening: {e}")
            raise
        finally:
            self._running = False
            await self.disconnect()

    async def _message_stream(self) -> AsyncGenerator[str, None]:
        """Stream messages from WebSocket with reconnection logic."""
        retry_count = 0
        max_retries = 5
        base_delay = 1.0

        while self._running and retry_count < max_retries:
            try:
                if not self.websocket:
                    await self.connect()
                    retry_count = 0  # Reset retry count on successful connection

                # Use asyncio.wait_for with timeout to periodically check _running
                while self._running:
                    try:
                        # Wait for message with 1 second timeout to check _running flag
                        message = await asyncio.wait_for(
                            self.websocket.recv(), timeout=1.0
                        )
                        if not self._running:
                            break
                        yield message
                    except asyncio.TimeoutError:
                        # Timeout is expected, just continue to check _running
                        continue
                    except ConnectionClosed:
                        # Connection closed, will be handled by outer exception handler
                        raise

            except ConnectionClosed:
                if not self._running:
                    # Don't attempt reconnection if we're shutting down
                    logger.info("WebSocket connection closed during shutdown")
                    break

                logger.warning(
                    "WebSocket connection closed, attempting to reconnect..."
                )
                retry_count += 1
                if retry_count < max_retries:
                    delay = base_delay * (2 ** (retry_count - 1))
                    logger.info(f"Retrying connection in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("Max retries exceeded, giving up")
                    break

            except WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break

    async def _duration_timeout(self) -> None:
        """Stop monitoring after specified duration."""
        await asyncio.sleep(self.duration)
        logger.info(f"Duration timeout ({self.duration}s) reached, stopping...")
        self._running = False
        self._stop_event.set()

    def _signal_handler(self) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        self._running = False
        self._stop_event.set()

        # Force close the WebSocket connection to break out of blocking reads
        if self.websocket:
            try:
                asyncio.create_task(self.websocket.close())
            except Exception:
                # Ignore errors during forced close
                pass


class StreamingMonitorClient(WebSocketClient):
    """WebSocket client for monitoring streaming metrics."""

    def __init__(self, duration: Optional[int] = None):
        """Initialize streaming monitor client.

        Args:
            duration: Optional duration in seconds to monitor
        """
        super().__init__("wss://streaming.api.restream.io/ws", duration)


class ChatMonitorClient(WebSocketClient):
    """WebSocket client for monitoring chat events."""

    def __init__(self, duration: Optional[int] = None):
        """Initialize chat monitor client.

        Args:
            duration: Optional duration in seconds to monitor
        """
        super().__init__("wss://chat.api.restream.io/ws", duration)
