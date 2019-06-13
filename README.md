# Rabbitholer

![img](./down_the_whole.png)


## Abstract

Rabbitholer is a very simple tool for communicating with a [RebbiMQ](https://en.wikipedia.org/wiki/RabbitMQ) server over [AMQP](https://en.wikipedia.org/wiki/Advanced_Message_Queuing_Protocol) protocol. It uses the [pika](https://pika.readthedocs.io/en/stable/) library for python and it offers convenient command line interface for sending and receiving messages to and from a RabbitMQ server instance. Rabbitholer is essentially a lightweight AMQP client.



I wrote this because I often had to debug RabbitMQ messages while working on different projects. The [web management plugin](https://www.rabbitmq.com/management.html) for RabbitMQ can be convenient but it doesn&rsquo;t really integrate with the other command line utilities I am used to ([GNU core utilities](https://www.gnu.org/software/coreutils/)). I&rsquo;ve designed Rabbitholer along the lines of the [minimalism idea](http://minifesto.org/) because I wanted it to be as versatile as possible. Easy integration with other utilities is a core design principle here.


## Install


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

| Argument           | Description                                                           |
|------------------ |--------------------------------------------------------------------- |
| `--server`, `-s`   | The IP of the RabbitMQ.\\ Standard port is assumed (5672).            |
| `--exchange`, `-e` | The name of the exchange to be\\ declared while connecting.           |
| `--queue`, `-q`    | The name of the queue to be\\ bound to the exchange while connecting. |
| `--routing`, `-r`  | The routing key to be used\\ for outgoing messages.                   |

Different arguments may influence different commands. For example, when receiving messages, the routing key does not play a role. The exchange will be declared as non-passive, non-durable and non-auto-delete and of type **fanout**. This means that the application can connect to an existing exchange. To note is however that if the exchange already exists, it must be of type **fanout**. The queue will be declared as non-auto-delete. Both the exchange and the queue have default names of &ldquo;general&rdquo;. These are the names that will be used unless specified otherwise thought the command line arguments. You can read more about the RabbitMQ exchanges and queues [here (complete reference guide)](https://www.rabbitmq.com/amqp-0-9-1-reference.html) and [here (quick explantion of the AMQP model)](https://www.rabbitmq.com/tutorials/amqp-concepts.html)



**send**:



**read**:



**monitor**:



**pipe**:


## Todos

[] Support for verbose logging [] Support for [MQTT](http://mqtt.org/) protocol. [] Support for configuration file.
