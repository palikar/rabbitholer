#!/usr/bin/env python
import argparse
import importlib
import locale
import os
import sys
import time

from rabbitholer.logger import debug
from rabbitholer.logger import debug_cyan
from rabbitholer.rabbit_dumper import RabbitDumper
from rabbitholer.version import VERSION


def play(args):
    with RabbitDumper(args) as dump, open(args.input) as fd :
        for msg in fd.read().splitlines():
            dump.send(msg)
            
        
def log_messgae(self, output, msg):
    with open(output, 'a') as fd:
        fd.write('{}\n'.format(msg))

def record(args):
    with RabbitDumper(args) as dump:
        debug_cyan('Recording messages...')
        dump.receive(lambda msg: log_message(args.output, msg))
