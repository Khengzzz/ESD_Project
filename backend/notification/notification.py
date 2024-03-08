#!/usr/bin/env python3
import amqp_connection
import json
import pika

payment_queue_name = 'Success_Queue'
refund_queue_name = 'Refund_Queue'

def receive_payment_log(channel):
    try:
        channel.basic_consume(queue=payment_queue_name, on_message_callback=callback, auto_ack=True)
        print('Payment Consumer: Consuming from queue:', payment_queue_name)
        channel.start_consuming()
    
    except pika.exceptions.AMQPError as e:
        print(f"Payment Consumer: Failed to connect: {e}")

    except KeyboardInterrupt:
        print("Payment Consumer: Program interrupted by user.")

def receive_refund_log(channel):
    try:
        channel.basic_consume(queue=refund_queue_name, on_message_callback=callback, auto_ack=True)
        print('Refund Consumer: Consuming from queue:', refund_queue_name)
        channel.start_consuming()
    
    except pika.exceptions.AMQPError as e:
        print(f"Refund Consumer: Failed to connect: {e}")

    except KeyboardInterrupt:
        print("Refund Consumer: Program interrupted by user.") 

def callback(channel, method, properties, body):
    print("\nReceived a log:")
    process_log(json.loads(body))

def process_log(log_data):
    print("Processing log:")
    print(log_data)

if __name__ == "__main__":
    print("Getting Connection")
    connection = amqp_connection.create_connection()
    print("Connection established successfully")
    channel = connection.channel()

    # Set up consumers for payment and refund queues
    receive_payment_log(channel)
    receive_refund_log(channel)
