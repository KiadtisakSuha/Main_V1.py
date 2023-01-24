import socket

HOST = '192.168.125.9'
PORT = 8000

# จากข้อ 1 : สร้าง socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# จากข้อ 4 : client ทำการเชื่อมต่อไปยัง server
s.connect((HOST, PORT))

# ส่งข้อมูลไปหา server
s.sendall(b'Hello World')

# รับข้อมูลที่ส่งมาจาก server
data = s.recv(1024)
print('received:', repr(data))