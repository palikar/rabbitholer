# Rabbitholer

![img](./down_the_whole.png)

![img](https://travis-ci.org/palikar/rabbitholer.svg?branch=master) ![img](https://pyup.io/repos/github/palikar/rabbitholer/shield.svg) ![img](https://pyup.io/repos/github/palikar/rabbitholer/python-3-shield.svg) ![img](https://coveralls.io/repos/github/palikar/rabbitholer/badge.svg?branch=master)


## Abstract

Rabbitholer is a very simple tool for communicating with a [RebbiMQ](https://en.wikipedia.org/wiki/RabbitMQ) server over [AMQP](https://en.wikipedia.org/wiki/Advanced_Message_Queuing_Protocol) protocol. It uses the [pika](https://pika.readthedocs.io/en/stable/) library for python and it offers convenient command line interface for sending and receiving messages to and from a RabbitMQ server instance. Rabbitholer is essentially a lightweight AMQP client.



I wrote this because I often had to debug RabbitMQ messages while working on different projects. The [web management plugin](https://www.rabbitmq.com/management.html) for RabbitMQ can be convenient but it doesn&rsquo;t really integrate with the other command line utilities I am used to ([GNU core utilities](https://www.gnu.org/software/coreutils/)). I&rsquo;ve designed Rabbitholer along the lines of the [minimalism idea](http://minifesto.org/) because I wanted it to be as versatile as possible. Easy integration with other utilities is a core design principle here.


## Installation

The package is available on [PyPi](https://pypi.org/project/rabbitholer/). Through pip it can be installed with:

```sh
pip install rabbitholer
```



Installation from the source is also possible. Just clone the repository and execute the `install` target from the Makefile

```cd
git clone https://github.com/palikar/rabbitholer
cd rabbitholer
make install
```


## Usage

A basic run of `rabitholer --help` gives:

```
usage: rabitholer [-h] [--version] [--verbose] [--very-verbose]
                  [--config CONFIG]
                  Command ...

Interact with RabbitMQ exhanges and queues

optional arguments:
  -h, --help            show this help message and exit
  --version, -V         Print veriosn inormation
  --verbose, -v         Print information about the execution.
  --very-verbose, -vv   Print a lot of information about the execution.
  --config CONFIG, -c CONFIG
                        Specify a configuration file. If not given,
                        '~/.config/rabbitholer/config.py' will be used

Commands:
  A list of the avialble commands

  Command
    send                Send a message to an exchange
    read                Send a messages to an exchange read from the standard
                        input.
    pipe                Create a named pipe connected to an exchange
    monitor             Monitor the messges on an exchange
    record              Record messages with specific routing key
    play                Replay previosly recorded massages
    list-msgs           Print recorded messages

```

Currently there are four supported commands: send, read, pipe, monitor, record and play (also an extra utility command &#x2013; list-msgs). All commands have certain arguments that are common between all of them. Those instruct the application how to connect to the server. They include:

| Argument           | Description                                                         |
|------------------ |------------------------------------------------------------------- |
| `--server`, `-s`   | The IP of the RabbitMQ. Standard port is assumed (5672).            |
| `--exchange`, `-e` | The name of the exchange to be declared while connecting.           |
| `--queue`, `-q`    | The name of the queue to be bound to the exchange while connecting. |
| `--routing`, `-r`  | The routing key to be used for outgoing messages.                   |

Different arguments may influence different commands. For example, when receiving messages, the routing key does not play a role. The exchange will be declared as non-passive, non-durable and non-auto-delete and of type **fanout**. This means that the application can connect to an existing exchange. To note is however that if the exchange already exists, it must be of type **fanout**. The queue will be declared as non-auto-delete. Both the exchange and the queue have default names of &ldquo;general&rdquo;. These are the names that will be used unless specified otherwise thought the command line arguments. If not specified, the routing key will be left as an empty string. You can read more about the RabbitMQ exchanges and queues [here (complete reference guide)](https://www.rabbitmq.com/amqp-0-9-1-reference.html) and [here (quick explantion of the AMQP model)](https://www.rabbitmq.com/tutorials/amqp-concepts.html).



**send**: Simply sends a message to the specified exchange with the specified routing key.

Intended to be used like:

```sh
rabbitholer send <msg>
```

Multiple messages can be send like:

```sh
rabbitholer send "<msg1>" "<msg2>" ...
```



**read**: Reads the standard output and dumps it on the specified exchange with the specified routing key. Each line is treated as a separate message.

The intended use is something like:

```sh
echo '<msg>' | rabbitholer read
```



**monitor**: Reads messages from a queue and dumps them on the standard output - each message is on separate line.

Example use:

```sh
rabbitholer read | grep "id:"
```



**pipe**: Creates a [named pipe](https://en.wikipedia.org/wiki/Named_pipe) connected to a running instance of the application. Any input to the pipe will be send as a message to the server. The intended use is:

```sh
rabbitholer pipe ./rabbithole
```

then you can do something like:

```sh
echo '<msg>' > ./rabbithole
```

**record**: Record incoming messages and save them in a file so that later they can be replayed. This command aims to be similar to [rosbag record](http://wiki.ros.org/rosbag/Commandline#rosbag_record). RabbitMQ doesn&rsquo;t really have the equivalent of a [rosbag](http://wiki.ros.org/rosbag/Commandline#rosbag_record) but the concept is extremely useful when it comes to messaging between applications. I wanted such functionality for a long time so I implemented it here. The usage is simple:

```sh
rabbitholer.py record [...] -o ~/car_msgs.p
```

This will save the recorded messages in the file `~/car_msgs.p`. The messages are recorded through [pickling](https://docs.python.org/3/library/pickle.html). Some meta information about the messages is saved (exchange, routing key, timestamps&#x2026;) so that they can be alter replayed exactly as they originally have been. The file can also be compressed with the `-c` flag. The used compression is [bzip2](https://en.wikipedia.org/wiki/Bzip2).

**play**: Replay messages that have been previously saved through the **record** command. As previously said, a timestamp of the messages is saved, so they will be replayed in a temporarily equivalent manner as they have been recorded (i.e. the relative time between two consecutive replayed messages will be same as it was during the recording of those messages). The command can be used like:

```sh
# those two are equivalent
rabbitholer.py play -o ~/car_msgs.p
rabbitholer.py play -i ~/car_msgs.p
```

**list-msgs**: List the messages that have been previously saved through the **record** command. This is a utility command used to examine the contents of a file with recorded messages.

```sh
rabbitholer.py list-msgs ~/car_msgs.p
```


## Message formatting

All commands that print messages in anyway (**play**, **list-msgs** and **monitor**) can take certain command line arguments to format the output. Those control how an individual message gets printed to the standard output. The arguments are:

```sh
--format FORMAT, -f FORMAT   Format string for the printed messages.
--json, -j                   Format the body of the message a json
```

`--format--` expects a format string that will be expanded during printing. The following table summarizes the possible tokens in the format string.

| Token | Meaning                                        |
| `%b`  | The body of the message                        |
| `%r`  | The routing key of the messages                |
| `%e`  | The exchange where the messages is coming from |
| `%h`  | The headers of the message                     |
| `%%`  | A literal &rsquo;%&rsquo; character            |

`--json` will parse the body of the messages as a JSON and will pretty printed to the standard output.


## Configuration

If present, rabbitholer will read (execute!) the file `~/.config/rabbitholer/config.py`. It servers as a configuration and **it is a full blown python script** so be careful what configuration you have in the file because potential malicious code could be executed. The file should contain a single dictionary object named `config` that will be used as configuration. The next snippets illustrates the possible options:

```python
config = {}

# the default server to be used
config['server'] = 'localhost'

# the default rabbitmq exahnge to be used for sending mesages
config['exchange'] = 'amq.topic'

# the default routing key to be used for sending and receiving mesages
config['routing_key'] = 'home'

# during recording of mesasges, the number of messages after which
# the messages will be synchronized with the file on the filesystem
config['pickler_cache_size'] = 50
```
