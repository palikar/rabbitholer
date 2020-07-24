import json

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


    def json_msg(self, msg):
        json_formated_msg = json.dumps(json.loads(msg), indent=2)
        print(json_formated_msg)
        

    def print_message(self, msg):

        if self.format:
            self.format_msg(msg)
        elif self.args.json:
            self.json_msg(msg.body)
        else:
            print(msg.body)
            
