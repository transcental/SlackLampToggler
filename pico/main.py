from machine import Pin
from servo import Servo
from time import sleep
from network import WLAN, STA_IF
from socket import socket
import urequests

def read_env():
    with open('env.txt', 'r') as f:
        ssid, password, server = f.read().split('\n')
        ssid = ssid.split('=')[1]
        password = password.split('=')[1]
        server = server.split('=')[1]
    return ssid, password, server
    

def connect():
    ssid, password, server = read_env()
    wlan = WLAN(STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print('Connected to Wi-Fi at IP:', ip)
    urequests.get(f'{server}/check?ip={ip}')
    return ip
    
def open_socket(ip):
    address = (ip, 80)
    connection = socket()
    connection.bind(address)
    connection.listen(1)
    print('Listening on:', ip)
    return connection
    
    
def serve(connection):
    global light_on
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        if request == '/toggle':
            toggle_lamp()
            lamp_state = 'on' if light_on else 'off'
            response = f'Toggled lamp {lamp_state}'
            status_line = 'HTTP/1.1 200 OK\n'
        elif request == '/on':
            turn_on()
            response = 'Turned on lamp'
            status_line = 'HTTP/1.1 200 OK\n'
        elif request == '/off':
            turn_off()
            response = 'Turned off lamp'
            status_line = 'HTTP/1.1 200 OK\n'
        else:
            response = 'Invalid request'
            status_line = 'HTTP/1.1 400 Bad Request\n'
        
        headers = 'Content-Type: text/plain\n\n'
        headers += 'Content-Length: ' + str(len(response)) + '\n'
        response = status_line + headers + response
        client.send(response.encode())
        client.close()

def toggle_lamp():
    global light_on
    if light_on:
        turn_off()
    else:
        turn_on()


def turn_off():
    global light_on
    light_on = False
    sg90_servo.move(0)


def turn_on():
    global light_on
    light_on = True
    sg90_servo.move(180)


sg90_servo = Servo(pin=12)  #To be changed according to the pin used
light_on = False
ip = connect()
connection = open_socket(ip)
serve(connection)

