#!/usr/bin/python3
import sys
from pika import BlockingConnection


def callback(ch, method, properties, body):
    print("Recebido:", body.decode())
    # ch.basic_ack(delivery_tag=method.delivery_tag) # se auto_ack = False


def consumer(channel, conection, queue_name):
    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=True)
    try:
        print('Esperando mensagens... CTRL+C para sair')
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    conection.close()


def publisher(channel, conection, queue_name, exchange='', body='hello world'):
    channel.basic_publish(
            exchange=exchange,
            routing_key=queue_name,
            body=body)
    conection.close()


def main(node_type, queue_name):
    conection = BlockingConnection()
    channel = conection.channel()
    channel.queue_declare(queue=queue_name)

    if node_type == 'consumer':
        consumer(channel, conection, queue_name)
    elif node_type == 'publisher':
        publisher(channel, conection, queue_name)
    else:
        print('node_type error')


def get(array, key, default=None):
    if isinstance(array, dict):
        return array.get(key, default)
    elif isinstance(array, list):
        try:
            return array[key]
        except IndexError:
            return default
    else:
        return default


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'USO: {sys.argv[0]} <node_type=consumer> <queue_name=queue>')

    node_type = 'consumer'
    # node_type = 'publisher'
    queue_name = 'queue'

    node_type = get(sys.argv, 1, default=node_type)
    queue_name = get(sys.argv, 2, default=queue_name)

    main(node_type, queue_name)
