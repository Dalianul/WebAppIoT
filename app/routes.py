from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time
import requests
from app import app 
from flask import redirect, render_template, request, session, url_for, Response
import serial
import threading
from datetime import datetime

app.secret_key = 'DH10'

global led_status
led_status = "OFF"
global temperature
temperature = "N/A"
messages = []

@app.route('/')
def main_page():
    led_status = session.get('led_status', 'OFF')
    message = session.pop('message', None)
    return render_template('index.html', title='Home', led_status=led_status, temperature=temperature, messages=messages, message=message)

@app.route("/get_temperature", methods=['GET'])
def get_temperature():
    global temperature
    return temperature

@app.route('/update_temperature', methods=['POST'])
def update_temperature():
    global temperature
    data = request.form['temperature']
    temperature = data
    return 'Temperature updated successfully'

@app.route('/led', methods=['POST'])
def led_control():
    ser = serial.Serial('COM10', 9600)
    action = request.form['action']
    if action == 'on':
        session['led_status'] = 'ON'
        ser.write(b'A')
    elif action == 'off':
        session['led_status'] = 'OFF'
        ser.write(b'S')
    return redirect(url_for('main_page'))

@app.route('/send_message', methods=['POST'])
def send_message():
    ser = serial.Serial('COM10', 9600)
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
    ser = serial.Serial('COM10', 9600)
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