import json
import pika
from PIL import Image
import logging


def resize_image(image_path, new_width, new_height):
    original_image = Image.open(image_path)
    resized_image = original_image.resize((new_width, new_height))
    resized_image.save(image_path)


def callback(ch, method, properties, body):
    logging.info(f" [x] Received {body.decode()}")
    task = json.loads(body)
    image_path = task["image_path"]
    new_width = task["new_width"]
    new_height = task["new_height"]
    resize_image(image_path, new_width, new_height)
    logging.info(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue="task_queue", durable=True)
logging.info(" [*] Waiting for messages. To exit press CTRL+C")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="task_queue", on_message_callback=callback)
channel.start_consuming()
