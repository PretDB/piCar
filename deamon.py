#!/usr/bin/python3
import serial
import socket


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.1)

print(get_host_ip())
print(socket.gethostname)
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((get_host_ip(), 9999))
soc.listen(5)

while True:
    sock, addr = soc.accept()
    data = sock.recv(1024)
    if not data:
        continue
    if data.decode('utf-8') == '0':
        ser.write(b'0')
        print('0')
    if data.decode('utf-8') == '1':
        ser.write(b'1')
        print('1')
    if data.decode('utf-8') == '2':
        ser.write(b'2')
        print('2')
    if data.decode('utf-8') == '3':
        ser.write(b'3')
        print('3')
    if data.decode('utf-8') == '4':
        ser.write(b'4')
        print('4')
    if data.decode('utf-8') == '5':
        ser.write(b'5')
        print('5')
    if data.decode('utf-8') == '6':
        ser.write(b'6')
        print('6')
