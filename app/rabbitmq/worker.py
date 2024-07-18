import json
import pika
from PIL import Image
import logging


def resize_image(image_path, new_width, new_height):
    try:
        original_image = Image.open(image_path)
        resized_image = original_image.resize((new_width, new_height))
        resized_image.save(image_path)
    except Exception as e:
        logging.error(f"Image processing error: {e}")
        raise


def callback(ch, method, properties, body):
    try:
        logging.info(f" [x] Received {body.decode()}")
        task = json.loads(body)
        image_path = task["image_path"]
        new_width = task["new_width"]
        new_height = task["new_height"]
        resize_image(image_path, new_width, new_height)
        logging.info(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        logging.error(f"Handling message error: {e}")


try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="task_queue", durable=True)
    logging.info(" [*] Waiting for messages. To exit press CTRL+C")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="task_queue", on_message_callback=callback)
    channel.start_consuming()
except pika.exceptions.AMQPConnectionError:
    logging.error("RabbitMQ connection error")
except Exception as e:
    logging.error(f"Something went wrong: {e}")
