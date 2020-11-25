from socket import *
import sys
from packet import Bucket, PacketUnwrapper
import time
from concurrent.futures import ThreadPoolExecutor
import wave

class Sender():
    def __init__(self,target,port,filename):
        self.socket = socket(AF_INET,SOCK_DGRAM)      
        self.socket.settimeout(3)
        self.filename = filename
        # self.host = target
        # self.port = port
        self.addr = (target,int(port))       
        self.execute()

    def execute(self):
        # print("tes")
        buf = 32767
        f = open(self.filename,"rb")
        datarray = []
        while True:
            data = f.read(buf)
            if data:
                datarray.append(Bucket(data,b'\x00',len(datarray),len(data).to_bytes(2,'big')))
            else:
                datarray[-1].setType(b'\x02')
                break
        
        num = 0
        while (datarray):
            recv_packet = None
            if len(datarray) > 1:
                data = datarray[0]
                # print(len(data))
                print(f"Sending packet {num}...")
                self.socket.sendto(data.buildPacket(),self.addr)
                print("Sent, waiting for ACK")
                try:
                    response, addrrec = self.socket.recvfrom(buf)
                    recv_packet = PacketUnwrapper(response)
                    if recv_packet.getType() == b'\x01': #ACK Package
                    # if recv_packet.seqnum == seqnum:
                        print("ACK packet received, sending next package, if any")
                        num -= -1
                        datarray.pop(0)
                except timeout:
                    print("Timeout on sending packet ", num)
                    print("Re-attempting...")
                except ConnectionResetError:
                    print("Connection reset. Peer is probably not open yet. Waiting for 5 seconds before reattempting...")
                    time.sleep(5)
            else: # Send FIN package
                try:
                    # print("Sending FIN package")
                    # print("Sending packet with seqnum : ", seqnum, bytes2hexstring(self.packets_queue[seqnum].data))
                    data = datarray[0]
                    print (f"Sending fin packet ({num})...")
                    self.socket.sendto(data.buildPacket(),self.addr)
                    print("Sent, waiting for FINACK....")
                    response, addrrec = self.socket.recvfrom(buf)
                    recv_packet = PacketUnwrapper(response)
                    # print("Received seqnum: ", recv_packet.getSeqnum())
                    if recv_packet.type == b'\x03':
                        # if recv_packet.seqnum == seqnum:
                        print("FIN-ACK packet received. Ending the current transmission")
                        break
                        # seqnum += 1
                except timeout:
                    print("Timeout on sending packet :", num)
                    print("Re-attempting...")
                except ConnectionResetError:
                    print("Connection reset. Peer is probably not open.")
            print()
        self.socket.close()
        f.close()



if __name__ == '__main__':
    # filename = input()
    # listtarget = sys.argv[1].split(',')
    # addresses = input()
    # port = int(input())
    # filename = input()
    # listtarget = addresses.split(',')
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     for target in listtarget:
    #         executor.submit(Sender,target,port,filename)
    try:
        filename = input("masukan nama file : ")
        print(filename)
        w = wave.open(filename,'r')
        print(w.getparams())
        w.close()
    except wave.Error as identifier:
        print(identifier)