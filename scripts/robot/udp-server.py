import socket
import serial

UDP_IP = "127.0.0.1" # Host IP - Change to IP address of R-Pi
UDP_PORT = 5005

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    #print("received message: %s" % data)
    if data != "":
        ser.write((data.decode()+'\n').encode())

