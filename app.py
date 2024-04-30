from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import serial
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'DH10'

global temperature
temperature = "N/A"
global message
message = "NULL"
messages = []
global cloud_led_state
cloud_led_state = 0
global message_valid
message_valid = 0
global schedule_valid
schedule_valid = 0
global on_time_str
on_time_str = "00:00"
global off_time_str
off_time_str = "00:00"

@app.route('/')
def main_page():
    cloud_led_state = session.get('cloud_led_state', 'OFF')
    message = session.pop('message', None)
    return render_template('index.html', title='Home', cloud_led_state=cloud_led_state, temperature=temperature, messages=messages, message=message, on_time_str=on_time_str, off_time_str=off_time_str)

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

@app.route('/get_led', methods=['GET'])
def get_led():
    global cloud_led_state
    return str(cloud_led_state)

@app.route('/post_led', methods=['POST'])
def led_control():
    global cloud_led_state
    action = request.form['action']
    if action == 'on':
        cloud_led_state = 1
        session['cloud_led_state'] = 'ON'
    elif action == 'off':
        cloud_led_state = 0
        session['cloud_led_state'] = 'OFF'
    return redirect(url_for('main_page'))

@app.route('/get_message', methods=['GET'])
def get_message():
    global message, message_valid
    if message_valid == 1:
        message_valid = 0
        return message
    else:
        return "NULL"

@app.route('/send_messages', methods=['POST'])
def send_messages():
    global message, message_valid, cloud_led_state
    message = request.form['message']
    messages.append(message)
    if message == 'AprindeLED':
        cloud_led_state = 1
        session['cloud_led_state'] = 'ON'
    elif message == 'StingeLED':
        cloud_led_state = 0
        session['cloud_led_state'] = 'OFF'
    message_valid = 1
    return redirect(url_for('main_page'))

@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    messages.clear()
    return redirect(url_for('main_page'))

# @app.route('/get_schedule', methods=['GET'])
# def get_schedule():
#     global on_time_str, off_time_str, schedule_valid
#     if schedule_valid == 1:
#         schedule_valid = 0
#         return jsonify({"off_time": off_time_str, "on_time": on_time_str})
#     else:
#         return "NULL_SCHEDULE"

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    global schedule_valid, on_time_str, off_time_str
    if request.method == 'POST':
        on_time_str = request.form['on_time']
        off_time_str = request.form['off_time']
    
    # Stocarea mesajului în sesiune
    session['message'] = f'Led setat pentru aprindere la ora {on_time_str} și pentru stingere la ora {off_time_str}.'

    schedule_valid = 1
    
    return redirect(url_for('main_page'))