import asyncio
import json

import pika, sys, os, time
from worker.main import handle_message

def main():
    delay = 1
    while True:
        connection = None
        try:
            # Создаем подключение
            params = pika.ConnectionParameters(
                host='localhost',
                heartbeat=30,
                blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # Проверяем существование очереди
            try:
                channel.queue_declare(queue='main_queue', passive=True)  # passive-True - проверить существования без создания
            except pika.exceptions.ChannelClosedByBroker as exc:
                print(f"Queue check failed: {exc}")
                raise  # Выходим из подключения, так как очереди нет

            # Обратная функция реагирующая на сообщения
            def callback(ch, method, properties, body):
                try:
                    message = json.loads(body.decode("utf-8"))
                    asyncio.run(handle_message(message))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                # ТУТ Разные конкретные исключения
                except Exception as exc:
                    print(f"Poison message or unrecoverable error: {exc}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            # Ограничиваем количество сообщений, обрабатываемых одновременно
            channel.basic_qos(prefetch_count=1)
            # Привязываем функцию к очереди
            channel.basic_consume(queue='main_queue', on_message_callback=callback)

            # Запускаем бесконечный цикл ожидания сообщений
            print(' [*] Waiting for messages')
            channel.start_consuming()

        except (
            pika.exceptions.AMQPConnectionError,
            pika.exceptions.ConnectionClosedByBroker,
            pika.exceptions.StreamLostError,
            pika.exceptions.AMQPChannelError
        ) as exc:
            print(f"Connection error: {exc}. Retrying in 5 seconds...")
            
            time.sleep(delay)
            delay = min(delay * 2, 30)

        # Закрываем соединение в случае исключений
        finally:
            if connection and connection.is_open:
                connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
