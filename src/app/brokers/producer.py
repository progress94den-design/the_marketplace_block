import asyncio
import json
from aio_pika import connect_robust, Message


# RABBIT_URL = "amqp://guest:guest@localhost/" # На локаке
RABBIT_URL = "amqp://guest:guest@rabbitmq:5672/" # В докере rabbitmq


async def send_registration_email(email: str, name: str):
    connection = await connect_robust(RABBIT_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("emails", durable=True)

        payload = {
            "type": "registration",
            "email": email,
            "name": name,
            "subject": "Welcome!",
            "body": f"Привет, {name}! Спасибо за регистрацию."
        }

        message = Message(
            body=json.dumps(payload).encode(),
            delivery_mode=2,  # сохраняется при падении Rabbit
            content_type="application/json"
        )

        await channel.default_exchange.publish(
            message,
            routing_key=queue.name
        )
        print(f"[producer] sent registration message for {email}")


if __name__ == "__main__":
    # asyncio.run(send_registration_email("test@example.com", "Ivan"))
    asyncio.run(send_registration_email())
