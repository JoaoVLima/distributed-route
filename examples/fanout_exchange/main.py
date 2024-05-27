#!/usr/bin/python3
import sys
from pika import BlockingConnection


def callback(ch, method, properties, body):
    print("Recebido:", body.decode())
    # ch.basic_ack(delivery_tag=method.delivery_tag) # se auto_ack = False


def consumer(channel, conection, exchange_name):
    res = channel.queue_declare(queue='', exclusive=True)
    queue = res.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue)
    channel.basic_consume(queue=queue,
                          on_message_callback=callback,
                          auto_ack=True)
    try:
        print('Esperando mensagens... CTRL+C para sair')
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    conection.close()


def publisher(channel, conection, exchange_name, body='hello world'):
    channel.exchange_declare(exchange=exchange_name,
                           exchange_type='fanout')
    channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=body)
    conection.close()


def main(node_type, exchange_name):
    conection = BlockingConnection()
    channel = conection.channel()
    channel.exchange_declare(exchange=exchange_name,
                             exchange_type='fanout')

    if node_type == 'consumer':
        consumer(channel, conection, exchange_name)
    elif node_type == 'publisher':
        publisher(channel, conection, exchange_name)
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
        print(f'USO: {sys.argv[0]} <node_type=consumer> <exchange_name=exchange>')

    node_type = 'consumer'
    # node_type = 'publisher'
    exchange_name = 'exchange'

    node_type = get(sys.argv, 1, default=node_type)
    exchange_name = get(sys.argv, 2, default=exchange_name)

    main(node_type, exchange_name)
