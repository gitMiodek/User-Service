import aio_pika
import asyncio


async def consumer():
    connection = await aio_pika.connect('amqp://guest:guest@rabbitmq')
    async with connection:
        queue_name = 'msg_que'
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        que = await channel.declare_queue(queue_name, auto_delete=True)
        async with que.iterator() as que_iterator:
            async for msg in que_iterator:
                async with msg.process():
                    print(msg.body)

if __name__== '__main__':
    asyncio.run(consumer())




