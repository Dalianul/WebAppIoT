from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import request, session
import serial
import requests
import time

COM_PORT = "COM10"
BAUD_RATE = 9600

ser = serial.Serial(COM_PORT, BAUD_RATE)

def send_data_to_serial(data):
    ser.write(data)

def send_notification():
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USERNAME = 'dalian.ardelean@gmail.com'
    SMTP_PASSWORD = 'twsj pdyk zvcn aaos'
    RECIPIENT_EMAIL = 'ardeleanharalambie21@gmail.com'

    message = MIMEMultipart()
    message['From'] = SMTP_USERNAME
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = 'Alertă! Inundație detectată!'

    # Construct the message body
    body = "A fost detectată o inundație la data și ora: " + time.strftime("%Y-%m-%d %H:%M:%S")
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = message.as_string()
        server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, text)
        server.quit()
        print("E-mail trimis cu succes!")
    except Exception as e:
        print("Eroare la trimiterea e-mailului:", e)

def read_serial_and_send_data():
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data.startswith("Temperatura celsius: "):
                temperature = data.split(": ")[1]
                try:
                    response = requests.post("http://localhost:5000/update_temperature", data={"temperature": temperature})
                    if response.status_code == 200:
                        print("Temperature data sent successfully to the Azure web app.")
                    else:
                        print(f"Failed to send temperature data to the Azure web app. Status code: {response.status_code}")
                except Exception as e:
                    print("Error sending temperature data:", e)
            elif data == "Inundatie detectata!":
                send_notification()
            
if __name__ == "__main__":
    print("Starting serial communication...")
    read_serial_and_send_data()
