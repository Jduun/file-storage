import pika
import json
import logging


def publish_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="task_queue", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="task_queue",
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    logging.info(f" [x] Sent {message}")
    connection.close()
