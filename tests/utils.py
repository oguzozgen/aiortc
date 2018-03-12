import asyncio
import logging
import os

from aiortc.utils import first_completed


class DummyIceTransport:
    def __init__(self, role):
        self.role = role


def dummy_dtls_transport_pair():
    transport_a, transport_b = dummy_transport_pair()

    transport_a.data = transport_a
    transport_a.rtp = transport_a
    transport_a.state = 'connected'
    transport_a.transport = DummyIceTransport(role='controlling')

    transport_b.data = transport_b
    transport_b.rtp = transport_b
    transport_b.state = 'connected'
    transport_b.transport = DummyIceTransport(role='controlled')

    return transport_a, transport_b


def dummy_transport_pair():
    queue_a = asyncio.Queue()
    queue_b = asyncio.Queue()
    return (
        DummyTransport(rx_queue=queue_a, tx_queue=queue_b),
        DummyTransport(rx_queue=queue_b, tx_queue=queue_a),
    )


class DummyTransport:
    def __init__(self, rx_queue, tx_queue):
        self.closed = asyncio.Event()
        self.rx_queue = rx_queue
        self.tx_queue = tx_queue

    async def close(self):
        self.closed.set()

    async def recv(self):
        data = await first_completed(self.rx_queue.get(), self.closed.wait())
        if data is True:
            raise ConnectionError
        return data

    async def send(self, data):
        if self.closed.is_set():
            raise ConnectionError
        await self.tx_queue.put(data)


def load(name):
    path = os.path.join(os.path.dirname(__file__), name)
    with open(path, 'rb') as fp:
        return fp.read()


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


logging.basicConfig(level=logging.DEBUG)
