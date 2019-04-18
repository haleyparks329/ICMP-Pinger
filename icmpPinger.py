from socket import *
import os
import sys
import struct
import time

ICMP_ECHO_REQUEST = 8

# make checksum of packet
def checksum(string):

    string = bytearray(string)
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count+1]) * 256 + (string[count])
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + (string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

# sending one ping
def sendPing(sock, destAddr, ID):

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    # dummy header with 0 checksum
    myChecksum = 0

    data = struct.pack("d", time.time())
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

    # Calculate checksum on data and dummy header.
    myChecksum = checksum(data + header)

    if sys.platform == 'darwin':
    # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    # socket sends packet and header
    sock.sendto(packet, (destAddr, 1))

# receiving one ping
def receivePing(sock, ID, timeout, destAddr):

    timeLeft = timeout

    while 1:
        selectStart = time.time()
        selectLength = (time.time() - selectStart)
        socket.settimeout(sock, 1)

        timeReceived = time.time()
        recPacket, addr = sock.recvfrom(1024)

        # Fetch ICMP header from IP packet

        icmpHeader = recPacket[20:28]
        type, code, myChecksum, recID, sequence = struct.unpack("bbHHh", icmpHeader)

        if (recID == ID) and (type != 8):
            doubleBytes = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + doubleBytes])[0]
            return (timeReceived - timeSent)

        else:
            return("Not the same ID.")

        timeLeft = timeLeft - selectLength

        if timeLeft <= 0:
            return("Request timed out.")

# do one ping
def doPing(destAddr, timeout):

    icmp = getprotobyname("icmp")

    # Creating Socket
    # SOCK_RAW is a powerful socket type. For more details: http://sock- raw.org/papers/sock_raw
    sock = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF # Return the current process i
    sendPing(sock, destAddr, myID)
    delay = receivePing(sock, myID, timeout, destAddr)
    sock.close()
    return delay

def ping(host, timeout=1):

    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")

    # Send ping requests to server separated by one second
    while 1 :
        delay = doPing(dest, timeout)
        print(delay)
        time.sleep(1)# one second
    return delay

ping("google.com")
#ping("127.0.1")
#ping("msstate.edu")
#ping("amazon.com")
