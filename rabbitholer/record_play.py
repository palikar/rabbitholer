#!/usr/bin/env python
from rabbitholer.logger import debug_cyan
from rabbitholer.rabbit_dumper import RabbitDumper


def play(args):
    with RabbitDumper(args) as dump, open(args.input) as fd:
        for msg in fd.read().splitlines():
            dump.send(msg)


def log_message(self, output, msg):
    with open(output, 'a') as fd:
        fd.write(f'{msg}\n')


def record(args):
    with RabbitDumper(args) as dump:
        debug_cyan('Recording messages...')
        dump.receive(lambda msg: log_message(args.output, msg))
