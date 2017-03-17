#/bin/python3

import socket
import os.path
import time
import mimetypes
from threading import Thread
from socketserver import ThreadingMixIn

class ClientThread(Thread):

    def __init__(self, ip, port, request, socket):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.request = request
        self.socket = socket
        print("New request from " + ip + ":" + str(port))

    def run(self):
        print('\033[0;33mRequest:\033[0m\n' + self.request.decode())
        tempRequest = str(self.request)
        data = []
        while len(tempRequest) > 0:
            data.append(tempRequest[:tempRequest.find("\\r\\n")])
            tempRequest = tempRequest[tempRequest.find("\\r\\n")+4:]

        data.pop()
        data.pop()

        data[0] = data[0][2:]
        data[0] = data[0].split(" ")

        hasReferer = False
        for split_data in data:
            if split_data[:7] == 'Referer':
                hasReferer = True

        if data[0][0] == "GET":
            self.do_GET(data[0][1], hasReferer)
        elif data[0][0] == "HEAD":
            self.do_HEAD(data[0][1])
        else:
            self.do_ERROR(501)

        self.socket.close()
        self.socket.detach()

    def do_GET(self, GET_request, hasReferer):
        path = os.path.dirname(os.path.realpath(__file__))+"/web"
        if '?' not in GET_request:
            if GET_request == "/":
                path += "/index.html"
            else:
                path += GET_request
        else:
            if GET_request[1:GET_request.find('?')] == "time":
                self.sendTime(GET_request[GET_request.find('=')+1:])
                return None
            elif GET_request[1:GET_request.find('?')] == "zone.html":
                self.generate_zone_html(GET_request[GET_request.find('=')+1:])
                return None
            else:
                path += GET_request[:GET_request.find('?')]

        """Check if file exists"""
        if path.find('.') == -1:
            print('\033[0;31m404 File not found:\033[0m')
            not_found_page = open('web/404.html', 'r').read()
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            http_response = 'HTTP/1.1 404 Not Found\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\nContent-Length: ' + str(
                len(not_found_page)) + '\r\nContent-Type: text/html\r\n\r\n'
            print('\033[0;31mResponse Header:\033[0m\n' + http_response)
            self.socket.send(http_response.encode())
            self.socket.sendall(not_found_page.encode())
        elif os.path.isfile(path):
            mime_type = mimetypes.guess_type(path)
            size = os.path.getsize(path)
            with open(path, "rb") as binary_file:
                data = binary_file.read()
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            http_response = 'HTTP/1.1 200 OK\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\nContenet-Length: ' + str(size) + '\r\nContent-Type: ' + mime_type[0] + '\r\n\r\n'
            print('\033[0;32mResponse Header:\033[0m\n' + http_response)
            print('\033[0;32mResponse Body Location:\033[0m\n' + path)
            self.socket.send(http_response.encode('utf-8'))
            self.socket.sendall(data)
        else:
            print('\033[0;31m404 File not found:\033[0m')
            if not hasReferer:
                not_found_page = open('web/404.html', 'r').read()
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            if not hasReferer:
                http_response = 'HTTP/1.1 404 Not Found\r\nServer: CRNS\r\nDate: ' + current_date +'\r\nConnection: close\r\nContent-Length: ' + str(len(not_found_page)) + '\r\nContent-Type: text/html\r\n\r\n'
                print('\033[0;31mResponse Header:\033[0m\n' + http_response)
                self.socket.send(http_response.encode())
                self.socket.sendall(not_found_page.encode())
            else:
                http_response = 'HTTP/1.1 404 Not Found\r\nServer: CRNS\r\nDate: ' + current_date +'\r\nConnection: close\r\n\r\n'
                print('\033[0;31mResponse Header:\033[0m\n' + http_response)
                self.socket.sendall(http_response.encode())

    def do_HEAD(self, HEAD_request):
        path = os.path.dirname(os.path.realpath(__file__)) + "/web"
        if '?' not in HEAD_request:
            if HEAD_request == "/":
                path += "/index.html"
            else:
                path += HEAD_request
        else:
            path += HEAD_request[:HEAD_request.find('?')]

        """Check if file exists"""
        if path.find('.') == -1:
            print('\033[0;31m404 File not found:\033[0m')
            not_found_page = open('web/404.html', 'r').read()
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            http_response = 'HTTP/1.1 404 Not Found\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\nContent-Length: ' + str(
                len(not_found_page)) + '\r\nContent-Type: text/html\r\n\r\n'
            print('\033[0;31mResponse Header:\033[0m\n' + http_response)
            self.socket.sendall(http_response.encode())
        elif os.path.isfile(path):
            mime_type = mimetypes.guess_type(path)
            size = os.path.getsize(path)
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            http_response = 'HTTP/1.1 200 OK\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\nContenet-Length: ' + str(
                size) + '\r\nContent-Type: ' + mime_type[0] + '\r\n\r\n'
            print('\033[0;32mResponse Header:\033[0m\n' + http_response)
            self.socket.sendall(http_response.encode('utf-8'))
        else:
            print('\033[0;31m404 File not found:\033[0m')
            not_found_page = open('web/404.html', 'r').read()
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            http_response = 'HTTP/1.1 404 Not Found\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\nContent-Length: ' + str(
                len(not_found_page)) + '\r\nContent-Type: text/html\r\n\r\n'
            print('\033[0;31mResponse Header:\033[0m\n' + http_response)
            self.socket.sendall(http_response.encode())

    def do_ERROR(self, error_num):
        print('\033[0;31m' + error_num + '\033[0m')
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        http_response = 'HTTP/1.1 ' + error_num + ' \r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\n\r\n'
        print('\033[0;31mResponse Header:\033[0m\n' + http_response)
        self.socket.sendall(http_response.encode())

    def sendTime(self, zone):
        my_time = self.get_time(zone)
        if my_time == '':
            print('\033[0;31m404 Not found:\033[0m')
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            http_response = 'HTTP/1.1 404 Not Found\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\n\r\n'
            print('\033[0;31mResponse Header:\033[0m\n' + http_response)
            self.socket.sendall(http_response.encode())
        else:
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            http_response = 'HTTP/1.1 200 OK\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\nContent-Length: ' + str(len(my_time)) + '\r\nContent-Type: text/plain\r\n\r\n'
            print('\033[0;32mResponse Header:\033[0m\n' + http_response)
            self.socket.send(http_response.encode())
            self.socket.sendall(my_time.encode())

    def get_time(self, zone):
        return {
            'cape_town': str((time.gmtime().tm_hour+2)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'washington_dc': str((time.gmtime().tm_hour-4)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'dubai': str((time.gmtime().tm_hour+4)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'amsterdam': str((time.gmtime().tm_hour+1)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'athens': str((time.gmtime().tm_hour+2)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'beijing': str((time.gmtime().tm_hour+8)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'berlin': str((time.gmtime().tm_hour+1)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'rio': str((time.gmtime().tm_hour-3)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'brussels': str((time.gmtime().tm_hour+1)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'budapest': str((time.gmtime().tm_hour+1)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'buenos_aires': str((time.gmtime().tm_hour-3)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'cairo': str((time.gmtime().tm_hour+2)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'sydney': str((time.gmtime().tm_hour+11)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'copenhagen': str((time.gmtime().tm_hour+1)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'tokyo': str((time.gmtime().tm_hour+9)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'taipei': str((time.gmtime().tm_hour+8)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'stockholm': str((time.gmtime().tm_hour+1)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'paris': str((time.gmtime().tm_hour+1)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'ottawa': str((time.gmtime().tm_hour-4)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'london': str(time.gmtime().tm_hour).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'new_york': str((time.gmtime().tm_hour-4)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'san_francisco': str((time.gmtime().tm_hour-7)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),
            'moscow': str((time.gmtime().tm_hour+3)%24).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2),

            'gmt': str(time.gmtime().tm_hour).zfill(2) + ':' + str(time.gmtime().tm_min).zfill(2) + ':' + str(time.gmtime().tm_sec).zfill(2).zfill(2),
        }.get(zone, '')

    def generate_zone_html(self, country):
        zone_page = open('web/zone.html', 'r').read()
        zone_page = zone_page.replace('{{zone}}', country)
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        http_response = 'HTTP/1.1 200 OK\r\nServer: CRNS\r\nDate: ' + current_date + '\r\nConnection: close\r\nContent-Length: ' + str(len(zone_page)) + '\r\nContent-Type: text/html\r\n\r\n'
        print('\033[0;31mResponse Header:\033[0m\n' + http_response)
        self.socket.send(http_response.encode())
        self.socket.sendall(zone_page.encode())


HOST, PORT = '', 80

try:
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    threads = []
    print("""

                CCCCCCCCCCCCCRRRRRRRRRRRRRRRRR   NNNNNNNN        NNNNNNNN   SSSSSSSSSSSSSSS
             CCC::::::::::::CR::::::::::::::::R  N:::::::N       N::::::N SS:::::::::::::::S
           CC:::::::::::::::CR::::::RRRRRR:::::R N::::::::N      N::::::NS:::::SSSSSS::::::S
          C:::::CCCCCCCC::::CRR:::::R     R:::::RN:::::::::N     N::::::NS:::::S     SSSSSSS
         C:::::C       CCCCCC  R::::R     R:::::RN::::::::::N    N::::::NS:::::S
        C:::::C                R::::R     R:::::RN:::::::::::N   N::::::NS:::::S
        C:::::C                R::::RRRRRR:::::R N:::::::N::::N  N::::::N S::::SSSS
        C:::::C                R:::::::::::::RR  N::::::N N::::N N::::::N  SS::::::SSSSS
        C:::::C                R::::RRRRRR:::::R N::::::N  N::::N:::::::N    SSS::::::::SS
        C:::::C                R::::R     R:::::RN::::::N   N:::::::::::N       SSSSSS::::S
        C:::::C                R::::R     R:::::RN::::::N    N::::::::::N            S:::::S
         C:::::C       CCCCCC  R::::R     R:::::RN::::::N     N:::::::::N            S:::::S
          C:::::CCCCCCCC::::CRR:::::R     R:::::RN::::::N      N::::::::NSSSSSSS     S:::::S
           CC:::::::::::::::CR::::::R     R:::::RN::::::N       N:::::::NS::::::SSSSSS:::::S
             CCC::::::::::::CR::::::R     R:::::RN::::::N        N::::::NS:::::::::::::::SS
                CCCCCCCCCCCCCRRRRRRRR     RRRRRRRNNNNNNNN         NNNNNNN SSSSSSSSSSSSSSS

                                =========== THE TIME SERVER ===========

    """)
    print("Serving HTTP Requests on port %s ..." % PORT)

    while True:
        listen_socket.listen(1)
        (client_connection, (ip,port)) = listen_socket.accept()
        newThread = ClientThread(ip, port, client_connection.recv(1024), client_connection)
        newThread.start()
        threads.append(newThread)

    for t in threads:
        t.join()

finally:
    listen_socket.close()