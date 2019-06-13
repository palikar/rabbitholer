import pika


class RabbitDumper:

    def __init__(self, exchange, queue, routing_key, server):

        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key
        self.server = server

        self.callback = None

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=server))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='fanout',
                                      passive=False,
                                      durable=False,
                                      auto_delete=False)

        self.channel.queue_declare(queue=self.queue, auto_delete=False)

        self.channel.queue_bind(exchange=self.exchange,
                                queue=self.queue,
                                routing_key=self.routing_key)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.destroy()

    def new_msg(self, **args):
        self.callback(args.get('body', '').decode("utf-8"))

    def send(self, msg):

        props = pika.spec.BasicProperties(expiration='30000')

        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=msg,
            properties=props)

    def receive(self, callback):
        self.callback = callback
        self.channel.basic_consume(
            queue=self.queue, on_message_callback=self.new_msg, auto_ack=True)
        self.channel.start_consuming()

    def destroy(self):
        self.channel.close()
        self.connection.close()
