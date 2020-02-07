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
usage: rabitholer [-h] [--version] [--verbose] Command ...

Interact with RabbitMQ exhanges and queues

optional arguments:
  -h, --help      show this help message and exit
  --version, -v   Print veriosn inormation
  --verbose, -vv  Print a lot of information about the execution.

Commands:
  A list of the avialble commands

  Command
    send          Send a message to an exchange
    read          Send a messages to an exchange read from the standard input.
    pipe          Create a named pipe connected to an exchange
    monitor       Monitor the messges on an exchange

```

Currently there are four supported commands: send, read, pipe and monitor. All commands have certain arguments that are common between all of them. Those instruct the application how to connect to the server. They include:

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
