#!/usr/bin/env python
import argparse
import importlib
import locale
import os
import sys
import time

from rabbitholer.logger import debug
from rabbitholer.logger import debug_cyan
from rabbitholer.logger import setup_logging
from rabbitholer.msg_printer import MessagePrinter
from rabbitholer.rabbit_dumper import RabbitDumper
from rabbitholer.record_play import list_messges
from rabbitholer.record_play import play
from rabbitholer.record_play import record
from rabbitholer.version import VERSION

VERSION_MSG = [
    f'rabbitholer version: {VERSION}',
    (
        'Python version: {}'
        .format(' '.join(line.strip() for line in sys.version.splitlines()))
    ),
    'Locale: {}'.format('.'.join(str(s) for s in locale.getlocale())),
]


DEFAULT_EXCHANGE = 'general'


def get_arg_parser():

    parser = argparse.ArgumentParser(
        prog='rabitholer',
        description='Interact with RabbitMQ exhanges and queues',
    )

    parser.add_argument(
        '--version', '-V', action='version',
        version=('\n'.join(VERSION_MSG)),
        help='Print veriosn inormation',
    )

    parser.add_argument(
        '--verbose', '-v', dest='verbose',
        action='store_true', default=False,
        help='Print information about the execution.',
    )

    parser.add_argument(
        '--very-verbose', '-vv', dest='very_verbose',
        action='store_true', default=False,
        help='Print a lot of information about the execution.',
    )

    parser.add_argument(
        '--config', '-c', dest='config',
        action='store', default=None,
        help='Specify a configuration file. If not given,\
 \'~/.config/rabbitholer/config.py\' will be used',
    )

    settings_parser = argparse.ArgumentParser(add_help=False)

    settings_parser.add_argument(
        '--exchange', '-e', dest='exchange',
        metavar='Exchange', action='store',
        required=False, default=DEFAULT_EXCHANGE,
        help='The exchange where\
                                 the message will be send',
    )

    settings_parser.add_argument(
        '--routing', '-r', action='store',
        metavar='Routing key', default=None,
        required=False, dest='routing_key',
        help='The routing key of the message',
    )

    settings_parser.add_argument(
        '--queue', '-q', action='store',
        metavar='Queue', default=None,
        required=False, dest='queue',
        help='Queue to bind to the exchange',
    )

    settings_parser.add_argument(
        '--server', '-s', action='store',
        metavar='Server', default=argparse.SUPPRESS,
        required=False, dest='server',
        help='The server where the\
                                 RabbiMQ server is running',
    )

    printer_parser = argparse.ArgumentParser(add_help=False)

    printer_parser.add_argument(
        '--format', '-f', action='store', default=None,
        required=False, dest='format',
        help='Format string for the printed messages.',
    )

    printer_parser.add_argument(
        '--json', '-j', action='store_true', default=False,
        required=False, dest='json',
        help='Format the body of the message a json',
    )

    printer_parser.add_argument(
        '--no-color', '-n', action='store_true', default=False, dest='no_color',
        help='Supress any color in the output',
    )

    printer_parser.add_argument(
        '--show-route', '-se', action='store_true', default=False, dest='show_routing_key',
        help='Display the the routing key of messages while printing in simple mode.',
    )

    subparsers = parser.add_subparsers(
        title='Commands', description='A list\
    of the avialble commands', dest='command', metavar='Command',
    )

    parser_send = subparsers.add_parser(
        'send',
        help='Send a message to an exchange',
        description='Send messages to an exchange or queue. Each word\
                                        after the command arguments is trated\
                                        as separate message',
        parents=[settings_parser],
    )
    parser_send.add_argument(
        'messages', nargs='*', default=None,
        help='A list of messages to send',
    )

    subparsers.add_parser(
        'read',
        help='Send a messages to an exchange\
                          read from the standard input.',
        description='Read the standard input\
                          line by line and send each line as a\
                          message to an exchange or a queue',
        parents=[settings_parser],
    )

    parser_pipe = subparsers.add_parser(
        'pipe',
        help='Create a named pipe connected\
                                        to an exchange', description='Create\
                                        a named pipe (in form of a file)\
                                        that is connected to an exchange\
                                        or queue. Everything dumped into\
                                        the pipe will be send\
                                        to the RabbitMQ server',
        parents=[settings_parser],
    )

    parser_pipe.add_argument(
        'pipe_name', default='./rabbitmq_pipe',
        nargs='?', help='The path to the named\
                             pipe to be created',
    )

    subparsers.add_parser(
        'monitor',
        help='Monitor the messges on an exchange',
        description='Receive messages from a queue\
                          of an exchange and dump them on the\
                          stadard output (one message per line).',
        parents=[settings_parser, printer_parser],
    )

    record_parser = subparsers.add_parser(
        'record',
        help='Record messages with specific routing key',
        description='Save the messages coming to an exchange with specific routing key to\
        a file on disk. The messages can then be replayed later.',
        parents=[settings_parser],
    )

    record_parser.add_argument(
        '--output', '-o', dest='output',
        action='store', required=True, default='rabbitmq_msgs.msg',
        help='The output file where the mesasges will be saved',
    )

    record_parser.add_argument(
        '--append', '-a', dest='append',
        action='store_true', required=False, default=False,
        help='Append the recorded messages to the output given file.',
    )

    record_parser.add_argument(
        '--compress', '-c', dest='compress',
        action='store_true', required=False, default=False,
        help='Compress the binary file where the messages are saved',
    )

    play_parser = subparsers.add_parser(
        'play',
        help='Replay previosly recorded massages',
        description='Read messages from a given file\
        and publish them on an exchange.',
        parents=[settings_parser], )

    play_parser.add_argument(
        '--input', '-i', '-o', dest='input',
        action='store', required=True, default='rabbitmq_msgs.msg',
        help='The input file where the mesasges were previously stored',
    )

    play_parser.add_argument(
        '--compress', '-c', dest='compress',
        action='store_true', required=False, default=False,
        help='Signify that the give mesage file is compressed',
    )

    list_parser = subparsers.add_parser(
        'list-msgs',
        help='Print recorded messages',
        description='Print the recorded messages in a file to the standard output',
        parents=[printer_parser],
    )

    list_parser.add_argument(
        'file', action='store',
        help='The input file where the mesasges were previously stored',
    )

    list_parser.add_argument(
        '--compress', '-c', dest='compress',
        action='store_true', required=False, default=False,
        help='Signify that the give mesage file is compressed',
    )

    return parser


def monitor(args):
    try:
        printer = MessagePrinter(args)
        with RabbitDumper(args) as dump:
            debug_cyan('Monitoring for messages:')
            dump.receive(printer.print_message)
    except KeyboardInterrupt:
        print('')
        sys.exit(0)


def read(args):
    try:
        with RabbitDumper(args) as dump:
            debug_cyan('Reading the standard ouput.')
            for line in sys.stdin:
                dump.send(line[0:-1])
    except KeyboardInterrupt:
        print('')
        sys.exit(0)


def pipe(args):
    path = args.pipe_name
    debug_cyan(f'Trying to open pipe on {path}')
    if os.path.exists(path) or os.path.isfile(path):
        print(
            'The given path is already exists: {}'
            .format(path),
        )
        sys.exit(1)

    with RabbitDumper(args) as dump:
        try:
            os.mkfifo(path)
            debug('Pipe creted')
            with open(path) as pipe_fd:
                while True:
                    message = pipe_fd.readline()
                    if message:
                        dump.send(message)
                        time.sleep(0.5)
        except OSError as err:
            print(
                'Error wile opening pipe: {}'
                .format(err),
            )
        finally:
            debug('Deliting trhe named pipe')
            os.remove(path)


def send(args):
    debug_cyan(
        'Trying to send messages: [{}]'
        .format(', '.join(args.messages)),
    )

    with RabbitDumper(args) as dump:
        for msg in args.messages:
            dump.send(msg)


COMMANDS = {}
COMMANDS['send'] = send
COMMANDS['monitor'] = monitor
COMMANDS['read'] = read
COMMANDS['pipe'] = pipe
COMMANDS['record'] = record
COMMANDS['play'] = play
COMMANDS['list-msgs'] = list_messges


def main():
    parser = get_arg_parser()
    args = parser.parse_args()

    setup_logging(args)

    debug(f'{VERSION_MSG[0]}')

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if not os.path.isdir(os.path.expanduser('~/.config/rabbitholer')):
        os.makedirs(os.path.expanduser('~/.config/rabbitholer'))

    if not os.path.isfile(
            os.path.expanduser('~/.config/rabbitholer/config.py'),
    ):
        with open(os.path.expanduser('~/.config/rabbitholer/config.py'), 'a'):
            pass

    config_file = '~/.config/rabbitholer/config.py'
    if args.config is not None:
        config_file = args.config

    config_file = os.path.expanduser(config_file)
    if not os.path.isfile(config_file):
        print(f'Invalid config file: {config_file}')
        sys.exit(1)

    debug(f'Config file: {config_file}')

    config_spec = importlib.util.spec_from_file_location(
        'config.module',
        config_file,
    )
    config = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config)

    if not hasattr(config, 'config'):
        debug('The configuration file does not define a config dict')

    for key in vars(args):
        value =  getattr(args, key)
        if value and config.config.keys():
            config.config[key] = value
            
    config.config.update((k, os.environ[k])
                     for k in config.config.keys() & os.environ.keys())

    args = argparse.Namespace(**config.config)

    debug(f'Command called: {args.command}')
    debug(f'Arguments: {vars(args)}')

    COMMANDS[args.command](args)


if __name__ == '__main__':
    main()
