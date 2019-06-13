#!/usr/bin/env python

import os
import sys
import argparse
import time
import locale

import pika

from rabbitholer.version import VERSION
from rabbitholer.rabbit_dumper import RabbitDumper
from rabbitholer.logger import setup_logging, debug_cyan, debug, debug_red

VERSION_MSG = [
    'code-manager version: {0}'.format(VERSION),
    ('Python version: {0}'
     .format(' '.join(line.strip() for line in sys.version.splitlines()))),
    'Locale: {0}'.format('.'.join(str(s) for s in locale.getlocale())),
]

DEFAULT_EXCHANGE = 'general'


def get_arg_parser():

    parser = argparse.ArgumentParser(
        prog="rabitholer",
        description='Interact with RabbitMQ exhanges and queues')

    parser.add_argument('--version', '-v', action="version",
                        version=('\n'.join(VERSION_MSG)),
                        help='Print veriosn inormation')

    parser.add_argument('--verbose', '-vv', dest='verbose',
                        action="store_true", default=False,
                        help='Print a lot of information about the execution.')

    settings_parser = argparse.ArgumentParser(add_help=False)

    settings_parser.add_argument('--exchange', '-e', dest='exchange',
                                 metavar='Exchange', action='store',
                                 required=False, default=DEFAULT_EXCHANGE,
                                 help='The exchange where\
                                 the message will be send')

    settings_parser.add_argument('--routing', '-r', action='store',
                                 metavar='Routing key', default='',
                                 required=False, dest='routing_key',
                                 help='The routing key of the message')

    settings_parser.add_argument('--queue', '-q', action='store',
                                 metavar='Queue', default='general',
                                 required=False, dest='queue',
                                 help='Queue to bind to the exchange')

    settings_parser.add_argument('--server', '-s', action='store',
                                 metavar='Server', default='taygeta',
                                 required=False, dest='server',
                                 help='The server where the\
                                 RabbiMQ server is running')

    subparsers = parser.add_subparsers(title='Commands', description='A list\
    of the avialble commands', dest='command', metavar='Command')

    parser_send = subparsers.add_parser('send',
                                        help='Send a message to an exchange',
                                        description='Send messages to an exchange or queue. Each word\
                                        after the command arguments is trated\
                                        as separate message',
                                        parents=[settings_parser])
    parser_send.add_argument('messages', nargs='*', default=None,
                             help='A list of messages to send')

    subparsers.add_parser('read',
                          help='Send a messages to an exchange\
                          read from the standard input.',
                          description='Read the standard input\
                          line by line and send each line as a\
                          message to an exchange or a queue',
                          parents=[settings_parser])

    parser_pipe = subparsers.add_parser('pipe',
                                        help='Create a named pipe connected\
                                        to an exchange', description='Create\
                                        a named pipe (in form of a file)\
                                        that is connected to an exchange\
                                        or queue. Everything dumped into\
                                        the pipe will be send\
                                        to the RabbitMQ server',
                                        parents=[settings_parser])
    parser_pipe.add_argument('pipe-name', default='./rabbitmq_pipe',
                             help='The path to the named pipe to be created')

    subparsers.add_parser('monitor',
                          help='Monitor the messges on an exchange',
                          description='Receive messages from a queue\
                          of an exchange and dump them on the\
                          stadard output (one message per line).',
                          parents=[settings_parser])

    return parser


def receive_msg(msg):
    print(msg)


def monitor(args):
    with RabbitDumper(args.exchange,
                      args.queue,
                      args.routing_key,
                      args.server) as dump:
        dump.receive(receive_msg)


def read(args):
    with RabbitDumper(args.exchange,
                      args.queue,
                      args.routing_key,
                      args.server) as dump:
        for line in sys.stdin:
            dump.send(line[0:-1])


def pipe(args):
    pipe_path = args.pipe
    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)
    with open(pipe_path, 'r') as pipe_fd:
        while True:
            message = pipe_fd.readline()
            if message:
                print(message, end="")
                time.sleep(0.5)


def send(args):
    with RabbitDumper(args.exchange,
                      args.queue,
                      args.routing_key,
                      args.server) as dump:

        for msg in args.messages:
            dump.send(msg)


COMMANDS = {}
COMMANDS['send'] = send
COMMANDS['monitor'] = monitor
COMMANDS['read'] = read
COMMANDS['pipe'] = pika


def main():
    parser = get_arg_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(0)

    if args.verbose:
        setup_logging(args)
        debug_cyan('Verbose mode.')

    debug('Command called: {}'.format(args.command))
    COMMANDS[args.command](args)


if __name__ == '__main__':
    main()
