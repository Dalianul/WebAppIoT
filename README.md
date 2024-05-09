Sistem de conducere pe bază de microcontroller (Arduino Uno) și tehnologii Cloud (Azure for Students) care va efectua următoarele funcții:
-Citirea temperaturii sistemului de la distanță.
-Controlul luminilor LED de la distanță.
-Transmiterea mesajelor prin internet către sistem.
-Detecția și alertarea inundațiilor.

How to run this demo:

Upload the code inside PS2N_1.0 on an Arduino Uno which needs to be connected to a computer via the serial in order to run the serial_communication script. 
Check the defines in order to figure out how to wire the setup.
Install the python requirements: python -m pip install -r requirements.txt.
Deploy the main folder (which contains app.py, templates and requirements.txt) to Azure.
Change the URL inside serial_communication.py to your azure url after deployment
Run: python serial_communication.py.

Proiect de echipa realizat de studentii Ardelean Dalian si Ardelean Haralambie!
