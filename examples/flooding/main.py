#!/usr/bin/python3
import sys
import uuid

from pika import BlockingConnection
from enum import Enum

States = Enum('State', ['STARTER', 'IDLE', 'VISITED', 'OK'])
State = States.IDLE
node_id = str(uuid.uuid4())
neighbor_nodes = []


def recebendo(origin, message, ch, neighbor_nodes):
    global State
    print(f'mensagem recebida: "{message}"')
    if State == States.IDLE:
        neighbors = neighbor_nodes[:]
        neighbors.remove(origin)
        envia(message, neighbors, ch)
        State = States.OK


def envia(message, neighbors, ch):
    global node_id
    message = node_id + ":" + message
    for node in neighbors:
        ch.basic_publish(exchange='',
                         routing_key=node,
                         body=message)


def espontaneamente(message, ch, neighbor_nodes):
    print("Im Starter!")
    envia(message, neighbor_nodes, ch)


def starter(channel, conection, body, neighbor_nodes):
    body = "STARTER:" + body
    for node in neighbor_nodes:
        channel.basic_publish(exchange='',
                              routing_key=node,
                              body=body)

    print(f'mensagem "{body}" enviada!')
    conection.close()


def callback(ch, method, properties, body):
    global State
    global node_id
    global neighbor_nodes

    body = body.decode().split(":")
    if len(body) < 2:
        print("body should be 'origin:message'")
    else:
        origin = body[0]
        message = body[1]
        if origin == "STARTER":
            espontaneamente(message, ch, neighbor_nodes)
        else:
            recebendo(origin, message, ch, neighbor_nodes)


def idle(channel, conection, node_id):
    channel.basic_consume(queue=node_id,
                          on_message_callback=callback,
                          auto_ack=True)
    try:
        print(f'{node_id} - esperando mensagens... CTRL+C para sair')
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    conection.close()


def main(node_type, node_id, body, neighbor_nodes):
    conection = BlockingConnection()
    channel = conection.channel()

    for node in neighbor_nodes:
        channel.queue_declare(queue=node, auto_delete=True)

    if node_type == 'idle':
        channel.queue_declare(queue=node_id, auto_delete=True)
        idle(channel, conection, node_id)
    elif node_type == 'starter':
        starter(channel, conection, body, neighbor_nodes)
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
        print(f'USO: {sys.argv[0]} <node_type=idle> <node_id=uuid()> [<node_fk>, <node_fk> ...]')
        print('or')
        print(f'USO: {sys.argv[0]} <node_type=starter> <body=hello_world> [<node_fk>, <node_fk> ...]')

    node_type = 'idle'
    # node_type = 'starter'
    node_id = str(uuid.uuid4())
    neighbor_nodes = []
    body = 'hello_world'

    node_type = get(sys.argv, 1, default=node_type)
    if node_type == 'idle':
        State = States.IDLE
        node_id = get(sys.argv, 2, default=node_id)
    elif node_type == 'starter':
        State = States.STARTER
        body = get(sys.argv, 2, default=body)

    if len(sys.argv) > 2:
        neighbor_nodes = sys.argv[3:]

    print(f'node_id = {node_id}')
    print(f'neighbor_nodes = {neighbor_nodes}')

    main(node_type, node_id, body, neighbor_nodes)
