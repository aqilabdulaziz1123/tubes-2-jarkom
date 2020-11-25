import struct


def checksum(data):
        if len(data) % 2 == 1:
            data += b'\x00'
        byte = b"%b" % data[0].to_bytes(1,'big')
        byte += b'%b' % data[1].to_bytes(1,'big')
        for i in range(2,len(data),2):
            hasil = b''
            current = data[i].to_bytes(1,'big')
            current += data[i+1].to_bytes(1,'big')
            for a,b in zip(byte,current):
                # print(f'{a} xor {b}')
                hasil += (a ^ b).to_bytes(1,'big')
                # print(f'jadi {hasil}')
            byte = hasil 
        return byte


class Bucket(): #builder packet  
    def __init__(self, data, _type, seqnum, length):
        # data = data to send
        # type = 0x00 -> data, 0x01 -> ACK, 0x02 ->FIN, 0x03 -> FINACK
        self.type = struct.pack('c', _type)
        self.seqnum = struct.pack('2s',seqnum.to_bytes(2,'big'))
        self.datalength = int.from_bytes(length,byteorder='big')    
        self.length = struct.pack('2s',length)
        if len(data) == int.from_bytes(self.length,byteorder='big'):
            # print(data)
            # print(self.datalength)
            self.data = struct.pack("{}s".format(int.from_bytes(self.length,byteorder='big')),data)
        else:
            # print(len(data))
            # print(int.from_bytes(self.length,byteorder='big'))
            print('exit')
            # exit(0)
        if _type == b'\x00' or _type == b'\x02':
            self.checksum = struct.pack('2s',checksum(b"%b%b%b%b" % (self.type,self.length,self.seqnum,self.data)))
        else:
            self.checksum = b'\x00\x00'
        # print(self.checksum)

    def __repr__(self):
        return f"{self.type}\n{self.seqnum}\n{self.length}\n{self.checksum}\n{self.data}"
    # def checksum(self):
    #     if len(self.data) % 2 == 1:
    #         self.data += b'\x00'
    #     byte = b"%b" % self.data[0].to_bytes(1,'big')
    #     byte += b'%b' % self.data[1].to_bytes(1,'big')
    #     for i in range(2,len(self.data),2):
    #         hasil = b''
    #         current = self.data[i].to_bytes(1,'big')
    #         current += self.data[i+1].to_bytes(1,'big')
    #         for a,b in zip(byte,current):
    #             print(f'{a} xor {b}')
    #             hasil += (a ^ b).to_bytes(1,'big')
    #             print(f'jadi {hasil}')
    #         byte = hasil 
    #     return byte
    
    def setType(self,_type):
        self.type = struct.pack('c',_type)
        self.checksum = struct.pack('2s',checksum(b"%b%b%b%b" % (self.type,self.length,self.seqnum,self.data)))
    
    def getData(self):
        return self.data

    def buildPacket(self):
        return struct.pack('c2s2s2s{}s'.format(self.datalength), self.type, self.length, self.seqnum, self.checksum, self.data)

    


class PacketUnwrapper():
    def __init__(self, received):
        # print(received)
        self.buffer = received
        self.type = (received[0]).to_bytes(1,'big')
        self.length = received[1:3]
        self.seq_num = received[3:5]
        self.checksum = received[5:7]
        # print(self.length)
        # print(int.from_bytes(self.length,byteorder='big'))
        self.data = self.getData()[4]

    def __repr__(self):
        return f"type:{self.type}\n{self.seq_num}\n{self.length}\n{self.checksum}\n"

    def getData(self):
        return struct.unpack('c2s2s2s{}s'.format(int.from_bytes(self.length,byteorder='big')),self.buffer)
        
    def getType(self):
        return self.type

    def getSeqnum(self):
        return self.seq_num

    def verify(self):
        cs = checksum(b"%b%b%b%b" % (self.type, self.length, self.seq_num,self.data))
        if cs != self.checksum:
            print("Verification failed, file is damaged")
            print(self.checksum)
            print(cs)
            return False
        else:
            print("Verification successful, file is in perfect condition")
            return True

    def write(self, filename):
        f = open(filename,'wb')
        f.write(self.data)
        f.close()
    
    def writeto(self,string):
        string += self.data
        return string

    


