#!/usr/bin/env python3
import amqp_connection
import json
import pika

payment_queue_names = ['Success_Queue', 'Failure_Queue']
refund_queue_name = 'Refund_Queue'

def receive_payment_log(channel, payment_queue_name):
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
    print("\nReceived a log by " + __file__)
    process_log(json.loads(body))
    print()

def process_log(log_data):
    print("Processing log:")
    print(log_data)

if __name__ == "__main__":
    print("Getting Connection")
    connection = amqp_connection.create_connection()
    print("Connection established successfully")
    channel = connection.channel()

    # Set up Notification microservice to subscribe to payment and refund queues and start consuming messages from each of them
    for payment_queue_name in payment_queue_names:
        receive_payment_log(channel, payment_queue_name)
        
    receive_refund_log(channel)
