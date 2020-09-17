import json


RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RED = '\033[38;5;197m'


class MessagePrinter:

    def __init__(self, args):
        self.args = args
        self.format = args.format
        self.color = not args.no_color
        self.show_route = args.show_routing_key

    def format_msg(self, msg):
        string = self.format

        # TODO: Fix this, this is bad
        string = string.replace('%%', '%')
        string = string.replace('%b', str(msg.body))
        string = string.replace('%r', str(msg.routing_key))
        string = string.replace('%e', str(msg.exchange))
        string = string.replace('%h', str(msg.props))

        sys.stdout.buffer.write(bytes(string + '\n', 'utf-8'))
        sys.stdout.buffer.flush()

    @staticmethod
    def json_msg(msg):
        try:
            json_formated_msg = json.dumps(json.loads(msg), indent=2)
            print(json_formated_msg)
        except json.JSONDecodeError:
            print(msg)

    def simple_print(self, msg):
        if self.color:
            preamble = RED + msg.routing_key + ':' + RESET if self.show_route else ''
        else:
            preamble = msg.routing_key + ':' if self.show_route else ''

        sys.stdout.buffer.write(bytes(preamble + msg.body + '\n', 'utf-8'))
        sys.stdout.buffer.flush()
        

    def print_message(self, msg):

        if self.format:
            self.format_msg(msg)
        elif self.args.json:
            self.json_msg(msg.body)
        else:
            self.simple_print(msg)
            
