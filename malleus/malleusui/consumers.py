import asyncio
import logging
import re
import ssl
from urllib.parse import parse_qs

from websockets.exceptions import InvalidURI, InvalidHandshake, ConnectionClosedError
from websockets.asyncio.client import connect

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.functional import cached_property
from django.conf import settings

from .labloader import LabLoader
from .incus.client import IncusClient

logger = logging.getLogger(__name__)

class WebsocketProxyConsumer(AsyncWebsocketConsumer):
    """Abstract base class for proxying websocket connections."""

    # This is the frequency of pinging we do to the target url.  Pinging seems
    # to confuse the code-server connection and it loses connection every 20
    # seconds, so for now we'll default to no pinging.
    PING_INTERVAL = None

    # This is the maximum size of frames going to/from the target url. We have
    # seen some frames larger than 1MiB being sent between the VS Code client and
    # code-server.
    MAX_SIZE = 2097152  # 2 MiB

    # These headers are passed through from the client to the target url.
    PASSTHROUGH_HEADERS = {
            'User-Agent',
            'Cookies',
    }

    async def get_target_url(self):
        return ""
    
    async def make_connection(self, target_url):
        # The requested url is not valid.
        if target_url is None:
            logger.warning('Denying websocket connection.')
            raise DenyConnection('The requested endpoint is not valid.')
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.load_cert_chain(settings.INCUS_CERT, settings.INCUS_KEY)

        # Connect to the target url.
        try:
            return await connect(
                    target_url, 
                    max_size=self.MAX_SIZE,
                    ping_interval=self.PING_INTERVAL,
                    subprotocols=self.scope['subprotocols'],
                    origin=self.request_headers.get('Origin'),
                    ssl=ssl_context,
            )
        except InvalidURI:
            logger.exception('The requested endpoint could not be reached.')
            raise DenyConnection('The requested endpoint could not be reached.')
        except InvalidHandshake:
            logger.exception('Communication with the target url was incoherent.')
            raise DenyConnection('Communication with the target url was incoherent.')
    

    async def connect(self):
        """Establish connections to both the client and the target url."""

        lab_id = self.scope["url_route"]["kwargs"]["lab_id"]
        instance_name = self.scope["url_route"]["kwargs"]["instance_name"]
        
        loader = LabLoader("../labs")
        loader.load()

        cleaned_lab_id = re.sub(r"[^a-zA-Z0-9_-]", "", lab_id)
        cleaned_instance = re.sub(r"[^a-zA-Z0-9_-]", "", instance_name)

        lab_data = loader.get(cleaned_lab_id)
        if lab_data is None:
            raise DenyConnection('Lab not found')
        
        lab_dict = lab_data.get_dict()

        client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)

        project_name = f"{self.scope["user"].username}--{cleaned_lab_id}"

        project = client.get_project(project_name)

        found = False
        for i in range(len(lab_dict['hosts'])):
            if found:
                continue
            host = lab_dict['hosts'][i]

            if host['hostname'] == cleaned_instance:
                found = True
                if host.get("console", False) == False:
                    raise DenyConnection("Console not allowed for " + cleaned_instance)
    
        if not found:
            raise DenyConnection("Instance not found")
        
        instance = project.get_instance(cleaned_instance)

        params = parse_qs(self.scope["query_string"].decode())

        console_info = instance.get_console(width=params.get('width', [80])[0], height=params.get('height', [24])[0])

        target_url = f"wss://{settings.INCUS_SERVER}:8443/1.0/operations/{console_info['id']}/websocket?secret={console_info['metadata']['fds']['control']}"
        self.control = await self.make_connection(target_url)

        target_url = f"wss://{settings.INCUS_SERVER}:8443/1.0/operations/{console_info['id']}/websocket?secret={console_info['metadata']['fds']['0']}"
        self.websocket = await self.make_connection(target_url)

        # Accept the client connection. Use the subprotocol negotiated with the
        # target url.
        await self.accept(self.websocket.subprotocol)

        # Forward packets from the target websocket back to the client.
        self.consumer_task = asyncio.create_task(self.consume_from_target())

    @cached_property
    def request_headers(self):
        return {
                h.decode('utf-8').title(): v.decode('utf-8')
                for h, v in self.scope['headers']
        }

    async def disconnect(self, close_code):
        """The websocket consumer is shutting down. Shut down the connection to
        the target url."""

        # Disconnect can be called before self.consumer_task is created.

        if hasattr(self, 'consumer_task'):
            self.consumer_task.cancel()

            # Let the task complete
            await self.consumer_task

    async def receive(self, text_data=None, bytes_data=None):
        """Forward packets from the client to the target url."""
        try:
            if text_data is not None:
                # Force into binary mode
                await self.websocket.send(text_data.encode())
            else:
                await self.websocket.send(bytes_data)
        except ConnectionClosedError:
            # The target probably closed the connection.
            logger.exception('The outgoing connection was closed by the target.')
            await self.close()

    async def consume_from_target(self):
        """A websocket consumer to forward data from the target url to the client."""
        try:
            async for data in self.websocket:
                if hasattr(data, 'decode'):
                    await self.send(bytes_data=data)
                else:
                    await self.send(text_data=data)
        except asyncio.exceptions.CancelledError:
            # This is triggered by the consumer itself when the client connection is terminating.
            logger.debug('Shutting down the websocket consumer task and closing the outgoing websocket.')
            await self.websocket.close()
        except ConnectionClosedError:
            # The target probably closed the connection.
            logger.exception('The outgoing connection was closed by the target.')
            await self.close()