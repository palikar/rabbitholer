import unittest
import sys

from io import StringIO
from unittest import mock
from contextlib import contextmanager

from rabbitholer.main import send
from rabbitholer.main import read
from rabbitholer.main import monitor
from rabbitholer.main import pipe


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

    @mock.patch('rabbitholer.main.RabbitDumper',
                autospec=True)
    def test_send(self, RabbitDumper):

        RabbitDumper.return_value.__enter__.return_value = mock.Mock()

        args = mock.Mock()
        args.messages = ['msg1', 'msg2']
        args.queue = 'general'
        args.exchange = 'general'
        args.routing_key = 'general'
        args.server = 'general'

        send(args)
        (RabbitDumper.return_value.__enter__
         .return_value.send.assert_any_call('msg1'))
        (RabbitDumper.return_value.__enter__
         .return_value.send.assert_any_call('msg2'))

    @mock.patch("sys.stdin", StringIO("msg1\nmsg2\n"))
    @mock.patch('rabbitholer.main.RabbitDumper',
                autospec=True)
    def test_read(self, RabbitDumper):

        RabbitDumper.return_value.__enter__.return_value = mock.Mock()

        args = mock.Mock()
        args.queue = 'general'
        args.exchange = 'general'
        args.routing_key = 'general'
        args.server = 'general'

        read(args)

        (RabbitDumper.return_value.__enter__
         .return_value.send.assert_any_call('msg1'))

        (RabbitDumper.return_value.__enter__
         .return_value.send.assert_any_call('msg2'))

    @mock.patch('rabbitholer.main.RabbitDumper',
                autospec=True)
    def test_monitor(self, RabbitDumper):
        RabbitDumper.return_value.__enter__.return_value = mock.Mock()

        args = mock.Mock()
        args.queue = 'general'
        args.exchange = 'general'
        args.routing_key = 'general'
        args.server = 'general'

        monitor(args)

        (RabbitDumper.return_value.__enter__
         .return_value.receive.assert_called_once())

        call = (RabbitDumper.return_value.__enter__
                .return_value.receive.call_args_list[0])
        callback, kwargs = call

        with captured_output() as (out, err):
            callback[0]('general')

        line = out.getvalue()
        self.assertEqual('general\n', line)


if __name__ == '__main__':
    unittest.main()
