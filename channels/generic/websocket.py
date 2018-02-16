import asyncio
import json
from typing import Any, Dict

from channels.generic.multiplexer import Demultiplexer

from asgiref.sync import async_to_sync

from ..consumer import AsyncConsumer, SyncConsumer
from ..exceptions import AcceptConnection, DenyConnection, InvalidChannelLayerError, StopConsumer


class WebsocketConsumer(SyncConsumer):
    """
    Base WebSocket consumer. Provides a general encapsulation for the
    WebSocket handling model that other applications can build on.
    """
    groups = []

    def websocket_connect(self, message):
        """
        Called when a WebSocket connection is opened.
        """
        try:
            for group in self.groups:
                async_to_sync(self.channel_layer.group_add)(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is unconfigured or doesn't support groups")
        try:
            self.connect()
        except AcceptConnection:
            self.accept()
        except DenyConnection:
            self.close()

    def connect(self):
        self.accept()

    def accept(self):
        """
        Accepts an incoming socket
        """
        super().send({"type": "websocket.accept"})

    def websocket_receive(self, message):
        """
        Called when a WebSocket frame is received. Decodes it and passes it
        to receive().
        """
        if "text" in message:
            self.receive(text_data=message["text"])
        else:
            self.receive(bytes_data=message["bytes"])

    def receive(self, text_data=None, bytes_data=None):
        """
        Called with a decoded WebSocket frame.
        """
        pass

    def send(self, text_data=None, bytes_data=None, close=False):
        """
        Sends a reply back down the WebSocket
        """
        if text_data is not None:
            super().send(
                {"type": "websocket.send", "text": text_data},
            )
        elif bytes_data is not None:
            super().send(
                {"type": "websocket.send", "bytes": bytes_data},
            )
        else:
            raise ValueError("You must pass one of bytes_data or text_data")
        if close:
            self.close(close)

    def close(self, code=None):
        """
        Closes the WebSocket from the server end
        """
        if code is not None and code is not True:
            super().send(
                {"type": "websocket.close", "code": code}
            )
        else:
            super().send(
                {"type": "websocket.close"}
            )

    def websocket_disconnect(self, message):
        """
        Called when a WebSocket connection is closed. Base level so you don't
        need to call super() all the time.
        """
        try:
            for group in self.groups:
                async_to_sync(self.channel_layer.group_discard)(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is unconfigured or doesn't support groups")
        self.disconnect(message["code"])
        raise StopConsumer()

    def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        pass


class JsonWebsocketConsumer(WebsocketConsumer):
    """
    Variant of WebsocketConsumer that automatically JSON-encodes and decodes
    messages as they come in and go out. Expects everything to be text; will
    error on binary data.
    """

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            self.receive_json(self.decode_json(text_data), **kwargs)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    def receive_json(self, content, **kwargs):
        """
        Called with decoded JSON content.
        """
        pass

    def send_json(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        super().send(
            text_data=self.encode_json(content),
            close=close,
        )

    @classmethod
    def decode_json(cls, text_data):
        return json.loads(text_data)

    @classmethod
    def encode_json(cls, content):
        return json.dumps(content)


class AsyncWebsocketConsumer(AsyncConsumer):
    """
    Base WebSocket consumer, async version. Provides a general encapsulation
    for the WebSocket handling model that other applications can build on.
    """
    groups = []

    async def websocket_connect(self, message):
        """
        Called when a WebSocket connection is opened.
        """
        try:
            for group in self.groups:
                await self.channel_layer.group_add(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is unconfigured or doesn't support groups")
        try:
            await self.connect()
        except AcceptConnection:
            await self.accept()
        except DenyConnection:
            await self.close()

    async def connect(self):
        await self.accept()

    async def accept(self):
        """
        Accepts an incoming socket
        """
        await super().send({"type": "websocket.accept"})

    async def websocket_receive(self, message):
        """
        Called when a WebSocket frame is received. Decodes it and passes it
        to receive().
        """
        if "text" in message:
            await self.receive(text_data=message["text"])
        else:
            await self.receive(bytes_data=message["bytes"])

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called with a decoded WebSocket frame.
        """
        pass

    async def send(self, text_data=None, bytes_data=None, close=False):
        """
        Sends a reply back down the WebSocket
        """
        if text_data is not None:
            await super().send(
                {"type": "websocket.send", "text": text_data},
            )
        elif bytes_data is not None:
            await super().send(
                {"type": "websocket.send", "bytes": bytes_data},
            )
        else:
            raise ValueError("You must pass one of bytes_data or text_data")
        if close:
            await self.close(close)

    async def close(self, code=None):
        """
        Closes the WebSocket from the server end
        """
        if code is not None and code is not True:
            await super().send(
                {"type": "websocket.close", "code": code}
            )
        else:
            await super().send(
                {"type": "websocket.close"}
            )

    async def websocket_disconnect(self, message):
        """
        Called when a WebSocket connection is closed. Base level so you don't
        need to call super() all the time.
        """
        try:
            for group in self.groups:
                await self.channel_layer.group_discard(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is unconfigured or doesn't support groups")
        await self.disconnect(message["code"])
        raise StopConsumer()

    async def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        pass


class AsyncJsonWebsocketConsumer(AsyncWebsocketConsumer):
    """
    Variant of AsyncWebsocketConsumer that automatically JSON-encodes and decodes
    messages as they come in and go out. Expects everything to be text; will
    error on binary data.
    """

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            await self.receive_json(await self.decode_json(text_data), **kwargs)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    async def receive_json(self, content, **kwargs):
        """
        Called with decoded JSON content.
        """
        pass

    async def send_json(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(
            text_data=await self.encode_json(content),
            close=close,
        )

    @classmethod
    async def decode_json(cls, text_data):
        return json.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content)


class AsyncJsonWebsocketDemultiplexer(Demultiplexer, AsyncJsonWebsocketConsumer):

    """
    JSON-understanding WebSocket consumer subclass that handles de-multiplexing
    streams using a "stream" key in a top-level dict and the actual payload
    in a sub-dict called "payload". This lets you run multiple streams over
    a single WebSocket connection in a standardised way.
    Incoming messages on streams are dispatched to consumers so you can
    just tie in consumers the normal way.
    """

    # Methods to INTERCEPT Client -> Stream Applications

    application_close_timeout = 5

    async def websocket_connect(self, message):
        """
        Connect and then inform each stream application.
        """
        await self.base_send({"type": "websocket.accept"})

        await self.send_to_all_upstream(message)

    async def receive_json(self, content, **kwargs):
        """
        Rout the message down the correct stream.
        """
        # Check the frame looks good
        if isinstance(content, dict) and "stream" in content and "payload" in content:
            # Match it to a channel

            stream = content["stream"]
            payload = content["payload"]

            # send it on to the application that handles this stream
            await self.send_upstream(
                stream=stream,
                message={
                    "type": "websocket.receive",
                    "text": await self.encode_json(payload)
                }
            )
            return
        else:
            raise ValueError("Invalid multiplexed **frame received (no channel/payload key)")

    # Methods to INTERCEPT Stream Applications -> Client

    async def websocket_send(self, message: Dict[str, Any], stream_name: str):
        """
        Capture downstream websocket.send messages from the stream applications.
        """
        text = message.get("text")
        # todo what to do on binary!

        json = await self.decode_json(text)
        data = {
            "stream": stream_name,
            "payload": json
        }

        await self.send_json(data)

    async def websocket_accept(self, message: Dict[str, Any], stream_name: str):
        """
        do not send this on.
        """
        pass

    async def websocket_disconnect(self, message):
        await self.send_to_all_upstream(message)
        try:
            # wait for the children to die before calling the
            # `disconnect method`
            await asyncio.wait(
                self._child_application_tasks.values(),
                return_when=asyncio.ALL_COMPLETED,
                timeout=self.application_close_timeout
            )
        except TimeoutError:
            # TODO warning!
            pass

        await super().websocket_disconnect(message)
