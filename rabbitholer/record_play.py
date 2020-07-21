import pickle
import sys
import time

from rabbitholer.logger import debug
from rabbitholer.logger import debug_cyan
from rabbitholer.rabbit_dumper import RabbitDumper
from rabbitholer.rabbit_dumper import Message
from rabbitholer.msg_printer import MessagePrinter


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


def log_message(msg):
    msg.timestamp = msg.props.timestamp if msg.props.timestamp else time.time()
    debug_cyan(f'Saving message from {msg.exchange} and with key {msg.routing_key}')
    pickler.push_msg(msg)


def record(args):
    try:
        with RabbitDumper(args) as dump, MsgPickler(args) as pickler:
            debug_cyan('Recording messages...')
            dump.receive(lambda msg: log_message(msg), full_msg=True)
    except KeyboardInterrupt:
        print('')
        sys.exit(0)


def list_messges(args):
    try:
        with open(args.file, 'rb') as fd:
            printer = MessagePrinter(args)
            while 1:
                msg = pickle.load(fd)
                if msg.body is None:
                    continue
                printer.print_message(msg)                
    except EOFError:
        pass

    
