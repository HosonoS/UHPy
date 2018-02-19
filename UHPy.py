import serial
import time

class UH():
    
    def __init__(self):
        self.UHAngle = []
        self.UHPR = []
        self.UHGyroAccelData = []
        #コネクトする
        #self.ser = serial.Serial('/dev/cu.usbserial-AK05D8TP', 115200,timeout=1)

        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.timeout = 1

        ports = list_ports.comports()

        devices = []

        for info in ports:
            devices.append(info.device)

        pattern = r"/dev/cu.usbserial"

        for i in range(len(devices)):
            match = re.match(pattern, devices[i])
            if match:
                self.ser.port = devices[i]
                print(str(devices[i]))
                break
        
        try:
            self.ser.open()
            print("open")

        except:
            print("can't open")


    def updatePhotosensors(self):
        try:
            self.ser.write(b'c')
            self.UHPR = list(map(lambda x: float(x), self.ser.readline().decode('utf-8').split("_")))

        except:
            pass

    def updateAngle(self):
        try:
            self.ser.write(b'A')
            self.UHAngle = list(map(lambda x: float(x), self.ser.readline().decode('utf-8').split("+")))
        
        except:
            pass

    def updateAnglePR(self):
        try:
            self.ser.write(b'C')
            bufferAnglePR = list(map(lambda x:float(x) ,self.ser.readline().decode('utf-8').split("+")))
            self.UHPR = bufferAnglePR[0:8]
            self.UHAngle = bufferAnglePR[8:]

        except:
            pass

    def updateUH3DGyroAccel(self):
        try:
            self.ser.write(b'a')
            self.UHGyroAccelData = list(map(lambda x:float(x),self.ser.readline().decode('utf-8').split("+")))

        except:
            pass

    def stimulate(self,padNum):
        try:
            padNum = str(padNum)
            ser.write((padNum).to_bytes(1,byteorder='big'))

        except:
            pass

    def setLevelUp(self):
        try:
            ser.write(b'h')

        except:
            pass

    def setLevelDown(self):
        try:
            ser.write(b'l')

        except:
            pass

    def vibrate(self):
        try:
            ser.write(b'b')

        except:
            pass

    def loop():
        stopFlag = True
        
        while stpoFlag:
            #以下にループさせたい処理を書いてください##
            
            ###########################################
            time.sleep(0.1)



if __name__ == '__main__':
    uhand = UH()
    stopflag = True

    while stopflag:
        uhand.updateUH3DGyroAccel()
        print(uhand.UHGyroAccelData)
        time.sleep(1)


