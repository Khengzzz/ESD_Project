import time
import pika
from os import environ

hostname = "localhost"  # default hostname
port = 5672             # default port
exchangename = "payment_topic"  # exchange name
exchangename2 = "refund_direct" 
exchangetype = "topic"  # use a 'topic' exchange to enable interaction
exchangetype2 = "direct"

def create_connection(max_retries=12, retry_interval=5):
    print('amqp_setup:create_connection')
    retries = 0
    connection = None
    
    while retries < max_retries:
        try:
            print('amqp_setup: Trying connection')
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
            print("amqp_setup: Connection established successfully")
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"amqp_setup: Failed to connect: {e}")
            retries += 1
            print(f"amqp_setup: Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

    if connection is None:
        raise Exception("amqp_setup: Unable to establish a connection to RabbitMQ after multiple attempts.")

    return connection

def create_channel(connection):
    print('amqp_setup:create_channel')
    channel = connection.channel()
    # Set up the exchange if the exchange doesn't exist
    print('amqp_setup:create exchange')
    channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True) # 'durable' makes the exchange survive broker restarts
    return channel

# Function to create queues
def create_queues(channel):
    print('amqp_setup:create_queues')
    create_success_queue(channel)
    create_failure_queue(channel)

# Function to create Success_Queue
def create_success_queue(channel):
    print('amqp_setup:create_success_queue')
    success_queue_name = 'Success_Queue'
    channel.queue_declare(queue=success_queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchangename, queue=success_queue_name, routing_key='*.success')

# Function to create Failure_Queue
def create_failure_queue(channel):
    print('amqp_setup:create_failure_queue')
    failure_queue_name = 'Failure_Queue'
    channel.queue_declare(queue=failure_queue_name, durable=True)
    channel.queue_bind(exchange=exchangename, queue=failure_queue_name, routing_key='*.failure')


def create_channel2(connection):
    print('amqp_setup:create_channel2')
    channel = connection.channel()
    # Set up the exchange if the exchange doesn't exist
    print('amqp_setup:create exchange2')
    channel.exchange_declare(exchange=exchangename2, exchange_type=exchangetype2, durable=True) # 'durable' makes the exchange survive broker restarts
    return channel

# Function to create queues for exchange 2
def create_queues2(channel):
    print('amqp_setup:create_queues2')
    create_refund_queue(channel)

# Function to create Refund_Queue
def create_refund_queue(channel):
    print('amqp_setup:create_refund_queue')
    refund_queue_name = 'Refund_Queue'
    channel.queue_declare(queue=refund_queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchangename2, queue=refund_queue_name, routing_key='#')

if __name__ == "__main__":
    connection = create_connection()
    channel = create_channel(connection)
    create_queues(channel)
    
    # For exchange 2 (refund_direct)
    channel2 = create_channel2(connection)
    create_queues2(channel2)

