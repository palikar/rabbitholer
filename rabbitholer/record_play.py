import time
import pickle
import sys

from rabbitholer.logger import debug_cyan
from rabbitholer.logger import debug
from rabbitholer.rabbit_dumper import RabbitDumper


class Message:

    def __init__(self, body, props, exchange, routing_key):
        self.body = body
        self.props = props
        self.exchange = exchange
        self.routing_key = routing_key


class MsgPickler:

    def __init__(self, output):
        self.output = output

        self.cache = []
        self.dirty = False

    def push_msg(self, msg):
        self.cache.append(msg)
        self.dirty = True
        if len(self.cache) > 20:
            self.flush()

    def flush(self):
        if not self.dirty:
            return
        with open(self.output, 'ab') as fd:
            debug_cyan(f'Flushing messages in {self.output}')
            for msg in self.cache:
                pickle.dump(msg, fd)
        self.cache.clear()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.flush()



def play(args):
    with  RabbitDumper(args) as dump, open(args.input, 'rb') as fd:
        try:
            while 1:
                msg = pickle.load(fd)
                debug(f'Sending message with key {msg.routing_key} to exchange {msg.routing_key}')
                dump.send(f'{msg.body}', headers=msg.props, key=msg.routing_key)
                time.sleep(0.3)
        except EOFError:
            pass

def log_message(pickler, method, props, msg):
    msg = Message(msg, props.headers, method.exchange, method.routing_key)
    msg.timestamp = props.timestamp

    debug_cyan(f'Saving message from {method.exchange} and with key {method.routing_key}')

    pickler.push_msg(msg)


def record(args):
    try:
        with RabbitDumper(args) as dump, MsgPickler(args.output) as pickler:
            debug_cyan('Recording messages...')
            dump.receive(
                lambda mthd, prop, msg: log_message(
                    pickler, mthd, prop, msg,
                ), full_msg=True,
            )
    except KeyboardInterrupt:
        print('')
        sys.exit(0)
