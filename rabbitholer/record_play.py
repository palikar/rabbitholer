import pickle

from rabbitholer.logger import debug_cyan
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
        self.dirty = False
        if len(self.cache) > 20:
            self.flush()

    def flush(self):
        if not self.dirty:
            return
        for msg in self.cache:
            with open(self.output, 'ab') as fd:
                pickle.dump(msg, fd)
        self.cache.clear()

    def __enter__(self):
        pass

    def __exit__(self):
        self.flush()


def play(args):
    with RabbitDumper(args) as dump, open(args.input) as fd:
        for msg in fd.read().splitlines():
            dump.send(msg)


def log_message(pickler, method, props, msg):
    pops_map = {}
    for field, val in props:
        pops_map[field] = val
    msg = Message(msg, pops_map, method.exchange, method.routing_ley)
    pickler.push_msg(msg)


def record(args):
    with RabbitDumper(args) as dump, MsgPickler(args.output) as pickler:
        debug_cyan('Recording messages...')
        dump.receive(lambda mthd, prop, msg: log_message(pickler, mthd, prop, msg))
