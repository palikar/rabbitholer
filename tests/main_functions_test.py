import sys
import unittest
from contextlib import contextmanager
from io import StringIO
from unittest import mock

from rabbitholer.main import read
from rabbitholer.main import send


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class CommandFunctions(unittest.TestCase):

    @mock.patch(
        'rabbitholer.main.RabbitDumper',
        autospec=True,
    )
    def test_send(self, RabbitDumper):

        RabbitDumper.return_value.__enter__.return_value = mock.Mock()

        args = mock.Mock()
        args.messages = ['msg1', 'msg2']
        args.queue = 'general'
        args.exchange = 'general'
        args.routing_key = 'general'
        args.server = 'general'

        send(args)
        (
            RabbitDumper.return_value.__enter__
            .return_value.send.assert_any_call('msg1')
        )
        (
            RabbitDumper.return_value.__enter__
            .return_value.send.assert_any_call('msg2')
        )

    @mock.patch('sys.stdin', StringIO('msg1\nmsg2\n'))
    @mock.patch(
        'rabbitholer.main.RabbitDumper',
        autospec=True,
    )
    def test_read(self, RabbitDumper):

        RabbitDumper.return_value.__enter__.return_value = mock.Mock()

        args = mock.Mock()
        args.queue = 'general'
        args.exchange = 'general'
        args.routing_key = 'general'
        args.server = 'general'

        read(args)

        (
            RabbitDumper.return_value.__enter__
            .return_value.send.assert_any_call('msg1')
        )

        (
            RabbitDumper.return_value.__enter__
            .return_value.send.assert_any_call('msg2')
        )


if __name__ == '__main__':
    unittest.main()
