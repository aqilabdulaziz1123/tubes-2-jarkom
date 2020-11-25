from socket import *
import sys
from packet import Bucket, PacketUnwrapper
import time
from concurrent.futures import ThreadPoolExecutor
import wave

CHUNK_SIZE = 32000 # For example, in bytes

class Streamer():
    # Streamer menggunakan protokol UDP
    def __init__(self,port,filename):
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.settimeout(3)
        self.port = int(port)
        self.subscriber = []
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.onplay = True

        #open audio file
        self.audio = wave.open(filename,'r')
        self.chunks = []
        #waiting subscriber
        self.executor.submit(self.load2bucket)
        self.executor.submit(self.waitSubscriber)
        self.executor.submit(self.sendChunk)

    def load2bucket(self):
        nChannels = self.audio.getnchannels()
        sampleWidth = self.audio.getsampwidth()
        nFrames = self.audio.getnframes()

        frameSize = nChannels * sampleWidth # In bytes
        frameCountPerChunk = CHUNK_SIZE / frameSize
        data = self.audio.readframes(int(frameCountPerChunk))
        num = 0
        while num < 100:
            print("loading"+ str(num) +"/"+ str(nFrames))
            self.chunks.append(Bucket(data,b'\x00',num,len(data).to_bytes(2,'big')))
            num += 1
        self.chunks[-1].setType(b'\x02')

    def waitSubscriber(self):
        #menunggu subscriber
        self.socket.bind(("",self.port))
        while self.onplay:
            _,addr = socket.recvfrom(32774)
            self.subscriber.append(addr)
            print("Subscriber baru dari "+addr)
            self.socket.sendto(self.audio.getparams(),addr)
            print("Mengirim metadata ke subsriber")

    def sendChunk(self):
        nChannels = self.audio.getnchannels()
        sampleWidth = self.audio.getsampwidth()
        frameRate = self.audio.getframerate()

        frameSize = nChannels * sampleWidth # In bytes
        frameCountPerChunk = CHUNK_SIZE / frameSize

        chunkTime = frameCountPerChunk / frameRate # In milliseconds.
        nowplay = 0
        while self.onplay:
            if(nowplay<len(self.chunks)):
                print("send chunk")
                startTime = time.time()
                for subs in self.subscriber:
                    self.send(self.chunks[nowplay],(subs,self.port))
                endTime = time.time()
                if endTime-startTime < chunkTime:
                    time.sleep(chunkTime - (endTime-startTime))
                nowplay+=1
            if(self.chunks[nowplay].type == b'\x02'):
                self.onplay = False


    def send(self,bucket,addr):
        recv_packet = None
        if  bucket.type == b'\x00':
            # print(len(data))
            print(f"Sending packet ...")
            self.socket.sendto(bucket.buildPacket(),addr)
            print("Sent, waiting for ACK")
            try:
                response, _ = self.socket.recvfrom(32774)
                recv_packet = PacketUnwrapper(response)
                if recv_packet.getType() == b'\x01': #ACK Package
                # if recv_packet.seqnum == seqnum:
                    print("ACK packet received, sending next package, if any")
            except timeout:
                print("Timeout on sending packet ")
                print("Re-attempting...")
            except ConnectionResetError:
                print("Connection reset. Peer is probably not open yet. Waiting for 5 seconds before reattempting...")
                time.sleep(5)
        else: # Send FIN package
            try:
                # print("Sending FIN package")
                # print("Sending packet with seqnum : ", seqnum, bytes2hexstring(self.packets_queue[seqnum].data))
                print (f"Sending fin packet...")
                self.socket.sendto(bucket.buildPacket(),addr)
                print("Sent, waiting for FINACK....")
                response, _ = self.socket.recvfrom(32774)
                recv_packet = PacketUnwrapper(response)
                # print("Received seqnum: ", recv_packet.getSeqnum())
                if recv_packet.type == b'\x03':
                    # if recv_packet.seqnum == seqnum:
                    print("FIN-ACK packet received. Ending the current transmission")
                    # seqnum += 1
            except timeout:
                print("Timeout on sending packet :")
                print("Re-attempting...")
            except ConnectionResetError:
                print("Connection reset. Peer is probably not open.")
        print()

Streamer(9090, 'example.wav')