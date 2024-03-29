import time
import pika
from os import environ

hostname = "localhost"  # default hostname
port = 5672             # default port
exchangename = "notification"  # exchange name
exchangetype = "topic"  # use a 'topic' exchange to enable interaction

# Function to establish a connection to RabbitMQ server
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

# Function to create a channel on the provided connection
def create_channel(connection):
    print('amqp_setup:create_channel')
    channel = connection.channel()
    # Set up the exchange if the exchange doesn't exist
    print('amqp_setup:create exchange')
    channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True) # 'durable' makes the exchange survive broker restarts
    return channel


# Function to create a single queue
def create_queue(channel):
    print('amqp_setup:create_queue')
    queue_name = 'Notification'
    channel.queue_declare(queue=queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    # Bind 4 unique routing_keys to determine consumer(s) of the notification
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.success')
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.failure')
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.refund')
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.subscribers')

if __name__ == "__main__":
    connection = create_connection()
    channel = create_channel(connection)
    create_queue(channel)