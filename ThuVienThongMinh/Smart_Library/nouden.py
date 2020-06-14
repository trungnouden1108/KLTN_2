import serial
import threading
import time, datetime
from .models import Check_book, Book
from django.core.exceptions import ObjectDoesNotExist

try:
    arduino = serial.Serial('COM3', timeout=1, baudrate=9600)
    connected = False
    id = ""
    a = ""
except:
    print('please check the port')
try:
    arduino1 = serial.Serial('COM6', timeout=1, baudrate=115200)

except:
    print('please check the port')

import socket
import serial
import time

HOST = '0.0.0.0'  # Thiết lập địa chỉ address
PORT = 8000  # Thiết lập post lắng nghe
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # cấu hình kết nối
s.bind((HOST, PORT))  # lắng nghe
s.listen(1)  # thiết lập tối ta 1 kết nối đồng thời

print("ok")
b4 = ""


def socket_recv():
    while True:
        client, addr = s.accept()
        while True:
            global b4
            b4 = ""
            time.sleep(0.09)
            data = client.recv(16)

            if data:
                b1 = data.decode('utf-8')
                b2 = b1.replace('\n', "")
                b3 = b2.replace('\r', "")
                b4 = b3.replace(" ", "")
                b5=b4.lower()
                print("b4", b4)
                try:
                    Book.objects.get(id_book=b5)
                    try:
                        Check_book.objects.get(id_bor=b5)
                    except ObjectDoesNotExist:
                        print("không hợp lệ")
                        client.send(b'O')
                except ObjectDoesNotExist:
                    pass
            else:
                break
        client.close()
        break;


def getsensordata():
    # st = list(str(arduino.readline(), 'utf-8'))
    # return (str(''.join(st[:])))
    try:
        arduino.open()
    except Exception as e:
        print("Exception: Opening serial port: " + str(e))
        global id, a
    start = datetime.datetime.now()
    second_start = start.second
    minute_start = start.minute
    hour_start = start.hour
    bef = hour_start * 3600 + minute_start * 60 + second_start
    while True:
        end = datetime.datetime.now()
        second_end = end.second
        minute_end = end.minute
        hour_end = end.hour
        atf = hour_end * 3600 + minute_end * 60 + second_end
        if (atf - bef >= 5):
            break;
        a = arduino.readline().decode()
        # b=str(a,encode='utf-8')
        time.sleep(0.25)
        c = a.replace(" ", "")
        e = c.replace("\r", "")
        id = e.replace("\n", "")
        print("com3", id)
        print(type(id))
        time.sleep(0.25)
        if id != "":
            time.sleep(0.125)
            break;
    arduino.close()
    return id


c2 = ""
def getidbook():
    # st = list(str(arduino.readline(), 'utf-8'))
    # return (str(''.join(st[:])))
    start = datetime.datetime.now()
    second_start = start.second
    minute_start = start.minute
    hour_start = start.hour
    bef = hour_start * 3600 + minute_start * 60 + second_start
    print("start")
    global c2
    try:
        arduino.open()
        print("com open")
    except:
        pass
    while True:
        end = datetime.datetime.now()
        second_end = end.second
        minute_end = end.minute
        hour_end = end.hour
        atf = hour_end * 3600 + minute_end * 60 + second_end
        if (atf - bef >= 4):
            break
        print(1)
        c2=""
        a5 = arduino.readline().decode('utf-8')
        if a5:
            c = a5.replace(" ", "")
            e = c.replace("\r", "")
            c2 = e.replace("\n", "")
            print("book", c2)
            if c2 != "":
                break
    print("com tắt")
    arduino.close()
    return c2


c1 = ""


def getiduser():
    # st = list(str(arduino.readline(), 'utf-8'))
    # return (str(''.join(st[:])))
    start = datetime.datetime.now()
    second_start = start.second
    minute_start = start.minute
    hour_start = start.hour
    bef = hour_start * 3600 + minute_start * 60 + second_start
    print("start")
    global c1
    try:
        arduino.open()
        print("com open")
    except:
        pass
    while True:
        end = datetime.datetime.now()
        second_end = end.second
        minute_end = end.minute
        hour_end = end.hour
        atf = hour_end * 3600 + minute_end * 60 + second_end
        if (atf - bef >= 4):
            break
        c1=""
        print(1)
        a5 = arduino.readline().decode('utf-8')
        if a5:
            c = a5.replace(" ", "")
            e = c.replace("\r", "")
            c1 = e.replace("\n", "")
            print("id_user", c1)
            if c1 != "":
                break

    print("com tắt")
    arduino.close()
    return c1


def day(a):
    c = 0
    if a == 0:
        c = 1000
    if a < 7 and a > 0:
        c = (a) * 1000
    elif a >= 7:
        c = (a) * 3000
    return c


id_check = ""
temp = ""


def checkbook():
    try:
        arduino.open()
    except Exception as e:
        print("Exception: Opening serial port: " + str(e))
    global id_check, temp
    time.sleep(0.5)
    temp = arduino.readline().decode()
    c = temp.replace(" ", "")
    e = c.replace("\r", "")
    id_check = e.replace("\n", "")
    print("f", id_check)
    if id_check != "":
        arduino.close()
        return id_check


def sendarduino_1():
    i = 0
    flag = 0
    try:
        arduino1.open()
    except Exception as e:
        print("Exception: Opening serial port: " + str(e))
        print("send")
    i = 0
    j = 0
    while (i < 1000):
        ledon()
        i += 1
    arduino1.close()


def sendarduino_2():
    i = 0
    try:
        arduino1.open()
    except Exception as e:
        print("Exception: Opening serial port: " + str(e))
        print("send")

    while (i < 1000):
        ledoff()
        i += 1
    arduino1.close()


def ledon():
    arduino1.write(b'1')


def ledoff():
    arduino1.write(b'0')
