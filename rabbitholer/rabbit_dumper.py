import pika

from rabbitholer.logger import debug
from rabbitholer.logger import debug_cyan


class RabbitDumper:

    def __init__(self, args):

        self.exchange = args.exchange
        self.queue = args.queue
        self.routing_key = args.routing_key
        self.server = args.server

        self.callback = None

        debug_cyan(f'Trying to open connection to {args.server}')
        try:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=args.server),
                )
            except:  # noqa: E722
                print('Establishing AMQP Connection failed! Check the server!')
                exit(1)

            debug('Connection opend')

            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=1)

        except pika.exceptions.ConnectionClosedByBroker as err:
            print(f'AMQP Connection closed by the broker: {err}')
            exit(1)
        except pika.exceptions.AMQPChannelError as err:
            print(f'AMQP channel error: {err}, stopping...')
            exit(1)
        except pika.exceptions.AMQPConnectionError as err:
            print(f'AMQP Connection closed: {err}')
            exit(1)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.destroy()

    def new_msg(self, _, _, _, body):  # noqa: F831
        debug_cyan(f'New message received: {body}')
        self.callback(body.decode('utf-8'))

    def send(self, msg):
        debug_cyan(f'Trying to send message: {msg}.')
        try:
            props = pika.spec.BasicProperties(expiration='30000')
            self.channel.basic_publish(
                exchange=self.exchange if self.exchange else '',
                routing_key=self.routing_key,
                body=msg,
                properties=props,
            )
            debug('Message send!')
        except pika.exceptions.ConnectionClosedByBroker as err:
            print(f'AMQP Connection closed by the broker: {err}')
        except pika.exceptions.AMQPChannelError as err:
            print(f'AMQP channel error: {err}, stopping...')
        except pika.exceptions.AMQPConnectionError as err:
            print(f'AMQP Connection closed: {err}')

    def receive(self, callback):
        self.callback = callback

        if self.queue:
            self.queue = self.channel.queue_declare(queue=self.queue, auto_delete=True).method.queue
        else:
            self.queue = self.channel.queue_declare(queue='', auto_delete=True).method.queue

        debug(f'Declared queue with name {self.queue}')

        if self.exchange is not None:
            self.channel.queue_bind(
                exchange=self.exchange,
                queue=self.queue,
                routing_key=self.routing_key,
            )
            debug('Queue was bound to the exchange {self.exchange} with\
            routing key {self.routing_key}')

        debug_cyan(f'Starting to recieve messages from {self.queue}')

        try:
            self.channel.basic_consume(
                queue=self.queue, on_message_callback=self.new_msg,
                auto_ack=True,
            )
            self.channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker as err:
            print(f'AMQP Connection closed by the broker: {err}.')
        except pika.exceptions.AMQPChannelError as err:
            print(f'AMQP channel error: {err}.')
        except pika.exceptions.AMQPConnectionError as err:
            print(f'AMQP Connection closed: {err}.')

    def destroy(self):
        debug_cyan('Closing connection to the broker.')
        self.channel.close()
        self.connection.close()
