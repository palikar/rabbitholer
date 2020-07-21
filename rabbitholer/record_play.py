import pickle
import sys
import time

from rabbitholer.logger import debug
from rabbitholer.logger import debug_cyan
from rabbitholer.rabbit_dumper import RabbitDumper


class Message:

    def __init__(self, body, props, exchange, routing_key):
        self.body = body
        self.props = props
        self.exchange = exchange
        self.routing_key = routing_key


class MsgPickler:

    def __init__(self, args):
        self.args = args

        self.output = args.output
        self.append = args.append

        self.cache = []
        self.dirty = True

        if not self.append:
            with open(self.output, 'wb'):
                pass

        msg = Message(None, None, None, None)
        msg.timestamp = time.time()
        self.cache.append(msg)

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
        self.dirty = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.flush()


def play(args):
    with RabbitDumper(args) as dump, open(args.input, 'rb') as fd:
        try:
            while 1:
                msg = pickle.load(fd)

                if msg.body is None:
                    prev_time = msg.timestamp
                    continue

                debug(f'Sending message with key {msg.routing_key} to exchange {msg.routing_key}')
                dump.send(f'{msg.body}', headers=msg.props, key=msg.routing_key)
                time.sleep(msg.timestamp - prev_time)
                prev_time = msg.timestamp
        except EOFError:
            pass


def log_message(pickler, method, props, msg):
    msg = Message(msg, props.headers, method.exchange, method.routing_key)
    msg.timestamp = props.timestamp if props.timestamp else time.time()
    debug_cyan(f'Saving message from {method.exchange} and with key {method.routing_key}')
    pickler.push_msg(msg)


def record(args):
    try:
        with RabbitDumper(args) as dump, MsgPickler(args) as pickler:
            debug_cyan('Recording messages...')
            dump.receive(
                lambda mthd, prop, msg: log_message(
                    pickler, mthd, prop, msg,
                ), full_msg=True,
            )
    except KeyboardInterrupt:
        print('')
        sys.exit(0)


def list_messges(args):
    pass
    
