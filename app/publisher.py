import json
import aio_pika


async def publisher(msg):
    connection = await aio_pika.connect('amqp://guest:guest@rabbitmq')

    async with connection:
        queue_name = 'msg_que'
        channel = await connection.channel()
        await channel.declare_queue(queue_name, auto_delete=True)
        message = aio_pika.Message(body=(json.dumps(msg.dict()).encode()))
        await channel.default_exchange.publish(message=message, routing_key=queue_name)
