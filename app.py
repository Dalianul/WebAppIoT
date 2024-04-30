from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from datetime import datetime, timedelta

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
global on_time_str
on_time_str = "00:00"
global off_time_str
off_time_str = "00:00"
global schedule_valid
schedule_valid = 0

@app.route('/')
def main_page():
    print(cloud_led_state)
    if cloud_led_state == 1:
        session['cloud_led_state'] = 'ON'
    elif cloud_led_state == 0:
        session['cloud_led_state'] = 'OFF'
    message = session.pop('message', None)
    return render_template('index.html', title='Home', cloud_led_state=cloud_led_state, temperature=temperature, messages=messages, message=message)

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
    elif action == 'off':
        cloud_led_state = 0
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
    messages.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S, ")) + "Mesaj: " + message)
    if message == 'AprindeLED':
        cloud_led_state = 1
    elif message == 'StingeLED':
        cloud_led_state = 0
    message_valid = 1
    return redirect(url_for('main_page'))

@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    messages.clear()
    return redirect(url_for('main_page'))

@app.route('/get_schedule', methods=['GET'])
def get_schedule():
    global on_time_str, off_time_str, schedule_valid,cloud_led_state
    # Splitting the on_time_str into hours and minutes
    on_time_parts = on_time_str.split(':')
    on_hour = int(on_time_parts[0])
    on_minute = int(on_time_parts[1])

    # Splitting the off_time_str into hours and minutes
    off_time_parts = off_time_str.split(':')
    off_hour = int(off_time_parts[0])
    off_minute = int(off_time_parts[1])

    # Now you have on_hour, on_minute, off_hour, and off_minute as integers
    print("On hour:", on_hour)
    print("On minute:", on_minute)
    print("Off hour:", off_hour)
    print("Off minute:", off_minute)

    # Obțineți data și ora curentă
    current_time = datetime.now()

    # Definiți un obiect timedelta pentru a adăuga 3 ore pentru a reprezenta fusul orar al serverului(US)
    offset = timedelta(hours=3)

    # Adăugați offsetul la data și ora curentă pentru a obține ora decalată
    current_time_offset = current_time + offset

    # Obțineți ora din noul obiect datetime decalat
    currentHour = current_time_offset.hour
    
    currentMin = datetime.now().minute

    print("Current hour:",currentHour)
    print("Current minute:",currentMin)

    if currentHour==on_hour and currentMin==on_minute and schedule_valid == 1:
        print("LED_SCHEDULE_ON!")
        cloud_led_state = 1
        schedule_valid = schedule_valid + 1
    elif currentHour==off_hour and currentMin==off_minute and schedule_valid == 2:
        print("LED_SCHEDULE_OFF!")
        cloud_led_state = 0
        schedule_valid = 0

    return jsonify({"off_time": off_time_str, "on_time": on_time_str})

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    global on_time_str, off_time_str, cloud_led_state,schedule_valid
    on_time_str = request.form['on_time']
    off_time_str = request.form['off_time']
    
    # Stocarea mesajului în sesiune
    # session['message'] = f'Led setat pentru aprindere la ora {on_time_str} și pentru stingere la ora {off_time_str}.'
    messages.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S, ")) + "Mesaj: " + "Led setat pentru aprindere la ora " + str(on_time_str) + " și pentru stingere la ora "+ str(off_time_str))
    schedule_valid = 1
    return redirect(url_for('main_page'))