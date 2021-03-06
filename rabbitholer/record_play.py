import bz2
import pickle
import sys
import time

from rabbitholer.logger import debug
from rabbitholer.logger import debug_cyan
from rabbitholer.msg_printer import MessagePrinter
from rabbitholer.rabbit_dumper import Message
from rabbitholer.rabbit_dumper import RabbitDumper
from rabbitholer.utils import sanitize_input_variable


class MsgPickler:

    def __init__(self, args):
        self.args = args

        self.output = sanitize_input_variable(args.output)
        self.append = args.append
        self.compress = args.compress

        self.cache = []
        self.cahce_dirty = True
        self.cache_size = args.pickler_cache_size if args.pickler_cache_size else 20

        self.file_descriptor = None

        if not self.append:
            with open(self.output, 'wb'):
                pass

        msg = Message(None, None, None, None)
        msg.timestamp = time.time()
        self.cache.append(msg)

    def push_msg(self, msg):
        self.cache.append(msg)
        self.cahce_dirty = True
        if len(self.cache) > self.cache_size:
            self.flush()

    def flush(self):
        if not self.cahce_dirty:
            return
        debug_cyan(f'Flushing messages in {self.output}')
        for msg in self.cache:
            pickle.dump(msg, self.file_descriptor)
            self.cache.clear()
            self.cahce_dirty = False

    def __enter__(self):
        self.file_descriptor = MsgPickler.open_file(self.output, 'a', self.args)
        return self

    def __exit__(self, *_):
        self.flush()
        self.file_descriptor.close()

    @staticmethod
    def open_file(file, mode, args):
        if args.compress:
            return bz2.BZ2File(file, mode)

        return open(file, mode + 'b')


def play(args):
    with RabbitDumper(args) as dump, MsgPickler.open_file(args.output, 'a', args) as file_descriptor:
        try:
            while 1:
                msg = pickle.load(file_descriptor)

                if msg.body is None:
                    prev_time = msg.timestamp
                    continue

                debug(f'Sending message with key {msg.routing_key} to exchange {msg.routing_key}')
                dump.send(f'{msg.body}', headers=msg.props, key=msg.routing_key)
                time.sleep(msg.timestamp - prev_time)
                prev_time = msg.timestamp
        except EOFError:
            pass


def log_message(pickler, msg):
    msg.timestamp = msg.props.timestamp if msg.props and msg.props.timestamp else time.time()
    debug_cyan(f'Saving message from {msg.exchange} and with key {msg.routing_key}')
    pickler.push_msg(msg)


def record(args):
    try:
        with RabbitDumper(args) as dump, MsgPickler(args) as pickler:
            debug_cyan('Recording messages...')
            dump.receive(lambda msg: log_message(pickler, msg), full_msg=True)
    except KeyboardInterrupt:
        print('')
        sys.exit(0)


def list_messges(args):
    try:
        with MsgPickler.open_file(args.file, 'r', args) as file_descriptor:
            printer = MessagePrinter(args)
            while 1:
                msg = pickle.load(file_descriptor)
                if msg.body is None:
                    continue
                printer.print_message(msg)
    except EOFError:
        pass
