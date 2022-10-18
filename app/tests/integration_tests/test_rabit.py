import aio_pika
import pytest

@pytest.mark.asyncio
async def test_an_async_function():
    connection = await aio_pika.connect('amqp://guest:guest@rabbitmq')
    async with connection as connection:

        assert connection
