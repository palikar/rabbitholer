#!/usr/bin/env python

import os
import sys
import argparse
import pika
import locale

from rabbitholer.version import VERSION

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

    parser.add_argument('--verbose', '-vv', dest='verbose', action="store_true",
                        default=False,
                        help='Print a lot of information about the execution.')

    
    settings_parser = argparse.ArgumentParser(add_help=False)

    settings_parser.add_argument('--exchange', '-e', dest='exchange', metavar='Exchange',
                                action='store', required=False, default=DEFAULT_EXCHANGE,
                                help='The exchange where the message will be send')
    
    settings_parser.add_argument('--routing', '-r', action='store', metavar='Routing key',
                                default='', required=False,
                                help='The routing key of the message')

    settings_parser.add_argument('--queue', '-q', action='store', metavar='Queue',
                                default='', required=False,
                                help='Queue to bind to the exchange')



    subparsers = parser.add_subparsers(title='Commands', description='A list\
    of the avialble commands', dest='command', metavar='Command')


        
    parser_send = subparsers.add_parser('send',
                                        help='Send a message to an exchange',
                                        description='Send messages to an exchange or queue. Each word\
                                        after the command arguments is trated as separate message',
                                        parents=[settings_parser])    
    parser_send.add_argument('messages', nargs='*', default=None,
                                help='A list of messages to send')
    



    parser_read = subparsers.add_parser('read',
                                        help='Send a messages to an exchange read from the standard input.',
                                        description='Read the standard input line by line and send each line\
                                        as a message to an exchange or a queue',
                                        parents=[settings_parser])


    
    parser_pipe = subparsers.add_parser('pipe',
                                        help='Create a named pipe connected to an exchange',
                                        description='Create a named pipe (in form of a file)\
                                        that is connected to an exchange or queue.\
                                        Everything dumped into the pipe will be send to the RabbitMQ server',
                                        parents=[settings_parser])    
    parser_pipe.add_argument('pipe-name', default='./rabbitmq_pipe',
                                help='The path to the named pipe to be created')


    
    parser_monitor = subparsers.add_parser('monitor',
                                        help='Monitor the messges on an exchange',
                                        description='Receive messages from a queue\
                                        of an exchange and dump them on the stadard output (one message per line).',
                                        parents=[settings_parser])

    return parser




def main():


    parser = get_arg_parser()

    args = parser.parse_args()


    if args.command == 'send':
        print(args.messages)
    

    
    
    # pipe_path = "/home/arnaud/rabit_pipe"


    # if not os.path.exists(pipe_path):
    #     os.mkfifo(pipe_path)

    # pipe_fd = open(pipe_path, 'r')

    
    # while True:
    #     message = pipe_fd.readline()
    #     if message:
    #         print(message, end="")
    #         time.sleep(0.5)

    # pipe_fd.close()
    
    
    # for line in sys.stdin:
    #     print(line, end="")

if __name__ == '__main__':
    main()
