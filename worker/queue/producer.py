import pika, time, json


def push_message(message_body: dict) -> bool:
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

            # Создаем или проверяем, что очередь есть
            channel.queue_declare(queue='callback_queue', durable=True, arguments={'x-queue-type': 'quorum'})

            # Публиуем сообщение
            channel.basic_publish(
                exchange='',
                routing_key='callback_queue', 
                body=json.dumps(message_body, ensure_ascii=False),  # Преобразуем словарь в JSON для передачи
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                    )
                )

            print(f" [x] Sent message to callback_queue {message_body}")
            return True

        except (
            pika.exceptions.AMQPConnectionError,
            pika.exceptions.ConnectionClosedByBroker,
            pika.exceptions.StreamLostError,
            pika.exceptions.AMQPChannelError
        ) as exc:
            print(f"Connection error: {exc}. Retrying in 5 seconds...")
            
            time.sleep(delay)
            delay = min(delay * 2, 30)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

        # Закрываем соединение в случае исключений
        finally:
            if connection and connection.is_open:
                connection.close()


if __name__ == '__main__':
    test_payload = {
        "status": "test",
        "message": "This is a test message from worker"
    }
    push_message(test_payload)