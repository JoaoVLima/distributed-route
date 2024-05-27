#!/usr/bin/python3
import sys
import uuid
from pika import BlockingConnection
from enum import Enum


class States(Enum):
    STARTER = 'STARTER'
    IDLE = 'IDLE'
    VISITED = 'VISITED'
    OK = 'OK'


class MessageTypes(Enum):
    TOKEN = 'T'  # passes the token forward
    BACKEDGE = 'B'  # notifies the detection of a “back-edge”
    RETURN = 'R'  # returns the token in case of local termination


class Node:
    state = ''
    message_type = ''
    id = ''
    connection = None
    channel = None

    def __init__(self, id=None, neighbor_nodes=None):
        self.id = id or str(uuid.uuid4())
        self.connection = BlockingConnection()
        self.channel = self.connection.channel()

        self.neighbor_nodes = neighbor_nodes or []

        for node in neighbor_nodes:
            self.channel.queue_declare(queue=node, auto_delete=True)

    def run(self):
        ...

    def send(self, message, from_starter):
        ...

    def receiving(self, origin, message):
        ...

    def callback(self, channel, method, properties, body):
        ...


class Starter(Node):
    neighbor_nodes = []
    message = 'Hello World'
    body = ''

    def __init__(self, id, neighbor_nodes):
        super(Starter, self).__init__(id, neighbor_nodes)
        self.state = States.STARTER

    def run(self):
        self.body = f'STARTER:T:{self.message}'
        for node in self.neighbor_nodes:
            self.channel.basic_publish(exchange='',
                                       routing_key=node,
                                       body=self.body)
        print(f'Sending message "{self.body}"!')
        self.connection.close()


class Idle(Node):
    neighbor_nodes = []

    def __init__(self, id, neighbor_nodes):
        super(Idle, self).__init__(id, neighbor_nodes)
        self.state = States.IDLE

        self.channel.queue_declare(queue=self.id, auto_delete=True)

    def run(self):
        self.channel.basic_consume(queue=node_id,
                                   on_message_callback=self.callback,
                                   auto_ack=True)
        try:
            print(f'waiting for messages...')
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        self.connection.close()

    def callback(self, channel, method, properties, body):
        body = body.decode().split(":")
        if len(body) < 3:
            print("body should be 'origin:type:message'")
        else:
            origin = body[0]
            type = body[1]
            message = body[2]
            if origin == States.STARTER and type == MessageTypes.TOKEN:
                self.send(message, from_starter=True)
                self.state = States.VISITED
            else:
                self.receiving(origin, message)

    def send(self, message, from_starter=False):
        if from_starter:
            print("I'm STARTER")
            print("sending message...")
        else:
            print("sending message...")

        message = f'{self.id}:{message}'
        for node in self.neighbor_nodes:
            self.channel.basic_publish(exchange='',
                                       routing_key=node,
                                       body=message)

    def receiving(self, origin, message):
        print(f'message received: "{origin}:{message}"')
        if self.state == States.IDLE:
            self.neighbor_nodes.remove(origin)
            self.send(message)
            self.state = States.OK


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
        print(f'USO: {sys.argv[0]} <node_type=starter> <message=hello_world> [<node_fk>, <node_fk> ...]')

    node_type = 'idle'  # or 'starter'
    node_id = str(uuid.uuid4())
    neighbor_nodes = []
    message = 'hello_world'

    if len(sys.argv) > 2:
        neighbor_nodes = sys.argv[3:]

    node_type = get(sys.argv, 1, default=node_type)
    if node_type == 'idle':
        node_id = get(sys.argv, 2, default=node_id)
        node = Idle(id=node_id, neighbor_nodes=neighbor_nodes)
    elif node_type == 'starter':
        message = get(sys.argv, 2, default=message)
        node = Starter(id=node_id, neighbor_nodes=neighbor_nodes)
        node.message = message

    print(f'node_id = {node.id}')
    print(f'node_type = {node_type}')
    print(f'neighbor_nodes = {node.neighbor_nodes}')

    node.run()
