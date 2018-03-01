import serial
import time
from serial.tools import list_ports
import re
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn import svm

class UH():
    
    def __init__(self):
        self.UHAngle = []
        self.UHPR = []
        self.UHGyroAccelData = []
        #self.ser = serial.Serial('/dev/cu.usbserial-AK05D8TP', 115200,timeout=1)

        self.X_train_std,self.y_train,self.X_test_std,y_test = None,None,None,None

        self.clfLogistic = LogisticRegression()
        self.clfSVM = svm.SVC()


        #Unlimitedhandとの接続に関する部分
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.timeout = 1

        ports = list_ports.comports()

        devices = []


        try:
            if sys.argv[1] == "manual":

                for info in ports:
                    devices.append(info.device)
                    
                print("以下のシリアルポートがパソコンに接続されています")
                for deviceName in devices:
                    print(deviceName)
        
                print("使いたいポート名を入力してください>>",end="")
                self.ser.port = input()
        
                try:
                    self.ser.open()
                    print("open")
        
                except:
                    print("can't open")
                    sys.exit()

        except:
            for info in ports:
                devices.append(info.device)

            self.ser.port = devices[2]
            
            try:
                print("デバイスと接続しています")
                self.ser.open()
    
            except:
                sys.exit()


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


    def gestureDataCollection(self):
        targetGesture1PR = np.array([0,0,0,0,0,0,0,0])
        targetGesture2PR = np.array([0,0,0,0,0,0,0,0])

        print("手を開いてください")

        #１つ目のジェスチャのデータ取得
        while len(targetGesture1PR) < 101:
            self.updatePhotosensors()
            PRbuff = np.array(self.UHPR)

            if len(PRbuff) < 8:
                pass
            
            else:
                targetGesture1PR = np.vstack((targetGesture1PR,PRbuff))
            
        targetGesture1PR = np.delete(targetGesture1PR,0,0)
            #targetGesture1PR.append(self.UHPR)
        
#        if len(targetGesture1PR) > 100:
#            difference = len(targetGesture1PR) - 100
#            for i in range(difference):
#                targetGesture1PR[i]
#
        print("3秒待機してください")
        time.sleep(3)

        print("手を閉じてください")
        
        #２つ目のジェスチャのデータ取得
        while len(targetGesture2PR) < 101:
            self.updatePhotosensors()
            PRbuff = np.array(self.UHPR)

            if len(PRbuff) < 8:
                pass

            else:
                targetGesture2PR = np.vstack((targetGesture2PR,PRbuff))

        targetGesture2PR = np.delete(targetGesture2PR,0,0)
        
        y1 = np.zeros(100,dtype=int)
        y2 = np.ones(100,dtype=int)

        X = np.r_[targetGesture1PR,targetGesture2PR]
        y = np.r_[y1,y2]

        ss = ShuffleSplit(n_splits=1,
                          train_size=0.7,
                          test_size=0.3,
                          random_state=0
                          )
        
        train_index, test_index = next(ss.split(X,y))

        X_train,X_test = X[train_index],X[test_index]
        self.y_train,self.y_test = y[train_index],y[test_index]

        sc = StandardScaler()
        self.X_train_std = sc.fit_transform(X_train)
        self.X_test_std = sc.transform(X_test)

    def gestureLogisticClassifier(self):
        self.clfLogistic = LogisticRegression()
        self.clfLogistic.fit(self.X_train_std,self.y_train)

    def gestureSVMClassifier(self):
        self.clfSVM.fit(self.X_train_std,self.y_train)
        

    def checkGesture(self):
        print("チェック用のジェスチャを入力してください")
        time.sleep(5)
        checkFlag = self.clfSVM.predict(self.UHPR)

        if checkFlag == 0:
            print("手を閉じています")

        else:
            print("手を開いています")

    def loop():
        stopFlag = True
        
        while stpoFlag:
            #以下にループさせたい処理を書いてください##
            
            ###########################################
            time.sleep(0.1)



if __name__ == '__main__':
    uhand = UH()
    uhand.gestureDataCollection()
    uhand.gestureSVMClassifier()
    uhand.checkGesture()


