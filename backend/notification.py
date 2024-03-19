#!/usr/bin/env python3
import amqp_connection
import json
import pika

# Necessary libraries for email notif
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

queue_name = 'Notification'

def receive_log(channel):
    try:
        channel.basic_consume(queue=queue_name, on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body, queue_name), auto_ack=True)
        print('Refund Consumer: Consuming from queue:', queue_name)
        channel.start_consuming()
    
    except pika.exceptions.AMQPError as e:
        print(f"Refund Consumer: Failed to connect: {e}")

    except KeyboardInterrupt:
        print("Refund Consumer: Program interrupted by user.") 

def callback(channel, method, properties, body, queue_name):
    print("\nReceived a log by " + __file__)
    process_log(json.loads(body), method.routing_key, queue_name)
    print()

def process_log(log_data, routing_key, queue_name):
    print("Processing log:")
    # Test code to identify queue which message was extracted from
    print("Message came from queue:", queue_name)
    print("Processing log with routing key:", routing_key)
    # Call email notif function
    send_email(log_data, routing_key, queue_name)

def send_email(log_data, routing_key, queue_name):
    # Sender details
    SENDER_EMAIL = 'esdprojectemail@gmail.com'  # Replace with your Gmail email address
    SENDER_PASSWORD = 'tupy hdfh errg rvbp'  # Replace with your Google Account app password

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    
    # Craft the email based on payment or refund recipient
    if routing_key == "*.success":  
        msg['Subject'] = 'Payment Success Notification'
        # One recipient
        msg['To'] = log_data["email"]  # Replace with the recipient email address
        
        # Form a custom notification string based on the log data
        notification_string = f"Notification: Payment "
        if 'payment_transaction_id' in log_data:
            notification_string += f"processed successfully. Transaction ID: {log_data['payment_transaction_id']}"
            
        # Can remove this if we scrapping failure scenario
        elif 'error_message' in log_data:
            notification_string += f"failed. Error: {log_data['error_message']}"

        # Attach the custom notif string to the email
        messageText = MIMEText(notification_string,'plain')
        msg.attach(messageText)

    elif routing_key == "*.failure":  
        msg['Subject'] = 'Payment Failure Notification'
        # One recipient
        msg['To'] = log_data["email"]  # Replace with the recipient email address
        
        # Form a custom notification string based on the log data
        notification_string = f"Notification: Payment "
        if 'payment_transaction_id' in log_data:
            notification_string += f"has not been processed successfully. Please try again later."
            
        # Can remove this if we scrapping failure scenario
        elif 'error_message' in log_data:
            notification_string += f"failed. Error: {log_data['error_message']}"

        # Attach the custom notif string to the email
        messageText = MIMEText(notification_string,'plain')
        msg.attach(messageText)

    elif routing_key == "*.refund": 
        
        msg['Subject'] = 'Refund Notification'
        # One recipient
        msg['To'] = log_data["email"]  # Replace with the recipient email address
        
        # Form a custom notification string based on the log data
        notification_string = f"Notification: Refund for booking ID {log_data['booking_id']} "
        if 'payment_transaction_id' in log_data:
            notification_string += f"processed successfully. Transaction ID: {log_data['payment_transaction_id']}"
            
        # Can remove this if we scrapping failure scenario
        elif 'error_message' in log_data:
            notification_string += f"failed. Error: {log_data['error_message']}"

        # Attach the custom notif string to the email
        messageText = MIMEText(notification_string,'plain')
        msg.attach(messageText)

    elif routing_key == "*.subscribers": 
            
        msg['Subject'] = 'Ticket Availability Notification'
            
        # Multiple recipients
        msg['To'] = log_data["email"] # Replace with the recipients email addresses
            
        # Form a custom notification string based on the log data
        notification_string = f"The screening now has seats available! Get your tickets now!"
                
        # Can remove this if we scrapping failure scenario
        if 'error_message' in log_data:
            notification_string += f"Error: {log_data['error_message']}"

        # Attach the custom notif string to the email
        messageText = MIMEText(notification_string,'plain')
        msg.attach(messageText)
            
        
    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo('Gmail')
        server.starttls()  # Start TLS encryption
        # Login to Gmail's SMTP server
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        # Send email
        if ',' in msg['To']:
            recipients = msg['To'].split(',')
        else:
            recipients = msg['To']
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
    finally:
        # Quit the SMTP server
        server.quit()
        
if __name__ == "__main__":
    print("Getting Connection")
    connection = amqp_connection.create_connection()
    print("Connection established successfully")
    channel = connection.channel()
        
    receive_log(channel)
