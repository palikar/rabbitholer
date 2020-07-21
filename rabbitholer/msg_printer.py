class MessagePrinter:

    def __init__(self, args):
        self.args = args
        self.format = args.format

    def format_msg(self, msg):
        string = self.format

        # TODO: Fix this, this is bad
        string = string.replace('%%', '%')
        string = string.replace('%b', str(msg.body))
        string = string.replace('%r', str(msg.routing_key))
        string = string.replace('%e', str(msg.exchange))
        string = string.replace('%h', str(msg.props))

        print(string)

    def print_message(self, msg):
        if not self.format:
            print(msg.body)
        else:
            self.format_msg(msg)
