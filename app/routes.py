from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time
from app import app 
from flask import redirect, render_template, request, session, url_for
import serial
import threading
from datetime import datetime

app.secret_key = 'DH10'

ser = serial.Serial('COM7', 9600)

global led_status
led_status = "OFF"
global temperature
temperature = "N/A"
messages = []

def read_from_serial():
    global temperature
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("Temperatura celsius: "):
                with app.app_context():
                    temperature = line.split(": ")[1]
            elif line == "Inundatie detectata!":
                send_notification()

threading.Thread(target=read_from_serial, daemon=True).start()

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

@app.route('/')
def main_page():
    led_status = session.get('led_status', 'OFF')
    message = session.pop('message', None)
    return render_template('index.html', title='Home', led_status=led_status, temperature=temperature, messages=messages, message=message)

@app.route("/get_temperature", methods=['GET'])
def get_temperature():
    global temperature
    return temperature

@app.route('/led', methods=['POST'])
def led_control():
    action = request.form['action']
    if action == 'on':
        ser.write(b'A')
        session['led_status'] = 'ON'
    elif action == 'off':
        ser.write(b'S')
        session['led_status'] = 'OFF'
    return redirect(url_for('main_page'))

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    ser.write(message.encode())
    messages.append(message)
    if message == 'A':
        session['led_status'] = 'ON'
    elif message == 'S':
        session['led_status'] = 'OFF'
    return redirect(url_for('main_page'))

@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    messages.clear()
    return redirect(url_for('main_page'))

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    if request.method == 'POST':
        on_time_str = request.form['on_time']
        off_time_str = request.form['off_time']
    
    # Parsare ora introdusă
        try:
            on_time = datetime.strptime(on_time_str, '%H:%M').time()
            off_time = datetime.strptime(off_time_str, '%H:%M').time()
        except ValueError:
            return "Invalid time format. Please use HH:MM format.", 400
    
    # Trimiterea datelor către Arduino
        ser.write(f'SET_SCHEDULE{on_time.hour},{on_time.minute},{off_time.hour},{off_time.minute}\n'.encode())

    # Stocarea mesajului în sesiune
        session['message'] = f'Led setat pentru aprindere la ora {on_time_str} și pentru stingere la ora {off_time_str}.'
    
        return redirect(url_for('main_page'))