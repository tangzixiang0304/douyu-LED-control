# -*- coding: utf-8 -*-

# __author__ = '_rieuse'
# __time__ = '2017.6.2'
# __github__ = 'https://github.com/rieuse'

import multiprocessing
import socket
import time
import re
import requests
from bs4 import BeautifulSoup
import serial.tools.list_ports

# plist = list(serial.tools.list_ports.comports())
# plist_0 = list(plist[0])
# serialName = plist_0[0]
# ser = serial.Serial(serialName, 9600, timeout=60)


# print(ser.is_open)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname("openbarrage.douyutv.com")
port = 8601
client.connect((host, port))

danmu = re.compile(b'txt@=(.+?)/cid@')


def sendmsg(msgstr):
    msg = msgstr.encode('utf-8')
    data_length = len(msg) + 8
    code = 689
    msgHead = int.to_bytes(data_length, 4, 'little') \
              + int.to_bytes(data_length, 4, 'little') + int.to_bytes(code, 4, 'little')
    client.send(msgHead)
    sent = 0
    while sent < len(msg):
        tn = client.send(msg[sent:])
        sent = sent + tn


def start(roomid):
    msg = 'type@=loginreq/username@=rieuse/password@=douyu/roomid@={}/\0'.format(roomid)
    sendmsg(msg)
    msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(roomid)
    sendmsg(msg_more)

    print('---------------{}---------------'.format(get_name(roomid)))
    ser = serial.Serial('COM4', 9600, timeout=60)
    print(ser.is_open)
    while True:
        data = client.recv(1024)
        danmu_more = danmu.findall(data)
        if not data:
            break
        else:
            for i in range(0, len(danmu_more)):
                print(danmu_more[0].decode(encoding='utf-8'))
                t = danmu_more[0].decode(encoding='utf-8')
                txt = t + '\n'
                print(txt, "长度", len(txt))
                print("test", len(txt) == 2)
                if len(txt) == 2:
                    print("进if了", t.encode('ascii'))
                    ser.write(t.encode("ascii"))
                    print("发送了", t.encode('ascii'))
                    # with open('danmu_1.txt', 'a') as fo:
                    #     try:
                    #         print(danmu_more[0].decode(encoding='utf-8'))
                    #         txt = danmu_more[0].decode(encoding='utf-8') + '\n'
                    #         print(txt,"长度",len(txt))
                    #         print("test",len(txt)==2)
                    #         if len(txt) == 2:
                    #             print("进if了")
                    #             ser.write(txt)
                    #             print("发送了",txt)
                    #
                    #         fo.writelines(txt)
                    #     except:
                    #         print("出错了")
                    #         continue


def keeplive():
    while True:
        msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\0'
        sendmsg(msg)
        time.sleep(10)


def get_name(roomid):
    r = requests.get("http://www.douyu.com/" + roomid)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup.find('a', {'class', 'zb-name'}).string


if __name__ == '__main__':
    room_id = input('input ID:')
    p1 = multiprocessing.Process(target=start, args=(room_id,))
    p2 = multiprocessing.Process(target=keeplive)
    p1.start()
    p2.start()
