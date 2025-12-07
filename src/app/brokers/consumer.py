import asyncio
import json
import aiosmtplib
from email.message import EmailMessage
from aio_pika import connect_robust

# RABBIT_URL = "amqp://guest:guest@localhost/" # На локаке
RABBIT_URL = "amqp://guest:guest@rabbitmq:5672/"  # В докере rabbitmq
OUTPUT_FILE = "sent_emails.log"


##############################################################
# Блок с иммитацией отправки сообщения на эмайл, запись в файл
##############################################################

def write_to_file(text: str):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(text)


async def save_email_to_file(data: dict):
    """Имитация отправки email"""
    text = f"""
==============================
TO: {data["email"]}
SUBJECT: {data["subject"]}
BODY: {data["body"]}
==============================
    """
    # асинхронная имитация I/O
    await asyncio.to_thread(write_to_file, text)


async def on_fake_message(message):
    async with message.process():
        data = json.loads(message.body.decode())
        await save_email_to_file(data)
        print(f"[worker] email saved for {data['email']}")


async def main_fake():
    while True:
        try:
            connection = await connect_robust(RABBIT_URL)
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)
                queue = await channel.declare_queue(
                    "emails",
                    durable=True
                )
                await queue.consume(on_fake_message)
                print("[worker] waiting for messages...")
                await asyncio.Future()
        except Exception as e:
            print(f"[worker] error: {e}")
            await asyncio.sleep(5)


#####################################
# Блок с отправкой сообщения на эмайл
#####################################

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"  # Почта от кого будут отправленно сообщение
SMTP_PASSWORD = "APP_PASSWORD"  # НЕ обычный пароль, App passwords который создается в настройках почты


async def send_real_email(data: dict):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = data["email"]
    message["Subject"] = data["subject"]
    message.set_content(data["body"])

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
    )


async def on_message(message):
    async with message.process():
        data = json.loads(message.body.decode())
        await send_real_email(data)
        print(f"[worker] email sent to {data['email']}")


async def main():
    while True:
        try:
            connection = await connect_robust(RABBIT_URL)
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)
                queue = await channel.declare_queue(
                    "emails",
                    durable=True,
                )
                await queue.consume(on_message)
                print("[worker] waiting for messages...")
                await asyncio.Future()
        except Exception as e:
            print(f"[worker] error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main_fake())  # Запуск фейковой отправки на почту сообщения
    # asyncio.run(main())  # Отправка сообщения на почту
