from socket import *
from struct import pack, unpack
import sys
from packet import PacketUnwrapper, Bucket

BUFFER = b""

# port = int(sys.argv[1])
port = int(input())
buf = 32774

s = socket(AF_INET, SOCK_DGRAM)
s.bind(("",port))

keterima = set([])


def process(data, addr):
    unwrapped = PacketUnwrapper(data)
    seq = unwrapped.getSeqnum()
    if seq not in keterima:
        keterima.add(seq)
        print(f"{seq} packet written")
        global BUFFER
        BUFFER = unwrapped.writeto(BUFFER)
    if(unwrapped.getType() == b'\x00'):
        if unwrapped.verify():
            print("Sending ACK....")
            ACKPack = Bucket(b"",b"\x01",int.from_bytes(unwrapped.getSeqnum(),byteorder='big'),b'\x00\x00').buildPacket()
            s.sendto(ACKPack,addr)
            return False
        else:
            return False
    else:
        if unwrapped.verify():
            print("Sending FINACK....")
            FINACKPack = Bucket(b"",b"\x03",int.from_bytes(unwrapped.getSeqnum(),byteorder='big'),b'\x00\x00').buildPacket()
            s.sendto(FINACKPack,addr)
            return True
        else:
            return False

while True:
    package,addr = s.recvfrom(buf)
    print("\nPackage received")
    if process(package, addr):
        break
    print()

f = open("./out/downloaded",'wb')
f.write(BUFFER)
print("\nFile downloaded")
f.close()

