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

from sklearn.metrics import accuracy_score

import csv

class UH():
    
    def __init__(self):
        self.UHAngle = []
        self.UHPR = []
        self.UHGyroAccelData = []
        self.UHQuaternion = []
        #self.ser = serial.Serial('/dev/cu.usbserial-AK05D8TP', 115200,timeout=1)

        self.X_train_std,self.y_train,self.X_test_std,self.y_test = None,None,None,None

        self.clfLogistic = LogisticRegression()
        self.clfSVM = svm.SVC()

        self.nowGesture = None

        #Unlimitedhandとの接続に関する部分
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.timeout = 1

        ports = list_ports.comports()

        devices = []


        #接続に関する部分（手動で行うかオートで行うか）
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

#        except IndexError:
#            print("No Device Connected")

        except:
            for info in ports:
                devices.append(info.device)

            self.ser.port = devices[2]
            
            try:
                print("デバイスと接続しています")
                self.ser.open()
    
            except:
                sys.exit()

    #フォトリフレクタの更新を行う関数
    def updatePhotosensors(self):
        try:
            self.ser.write(b'c')
            self.UHPR = list(map(lambda x: float(x), self.ser.readline().decode('utf-8').split("_")))

        except:
            pass
    #角度の値の更新を行う関数
    def updateAngle(self):
        try:
            self.ser.write(b'A')
            self.UHAngle = list(map(lambda x: float(x), self.ser.readline().decode('utf-8').split("+")))
        
        except:
            pass

    #フォトリフレクタと角度の値の更新を同時に行う
    def updateAnglePR(self):
        try:
            self.ser.write(b'C')
            bufferAnglePR = list(map(lambda x:float(x) ,self.ser.readline().decode('utf-8').split("+")))
            self.UHPR = bufferAnglePR[0:8]
            self.UHAngle = bufferAnglePR[8:]

        except:
            pass

    #加速度と角速度の値を更新する
    def updateUH3DGyroAccel(self):
        try:
            self.ser.write(b'a')
            self.UHGyroAccelData = list(map(lambda x:float(x),self.ser.readline().decode('utf-8').split("+")))

        except:
            pass

    #クォータニオンの値を更新する
    def updateQuaternion(self):
        try:
            self.ser.write(b'q')
            self.UHQuaternion = list(map(lambda x:float(x),self.ser.readline().decode('utf-8').split("+")))

        except:
            pass

    #クォータニオンの値をリセットする
    def resetQuaternion(self):
        try:
            self.ser.write('r')

        except:
            pass

    #降った動作を識別(未完成)
    def shakeCheck(self):
        try:
            self.updateQuaternion()
            buff1 = np.array(self.UHQuaternion)
            time.sleep(0.5)
            self.updateQuaternion()
            buff2 = np.array(self.UHQuaternion)
            
            print(np.dot(buff1,buff2))

        except:
            pass

    #電気刺激を行う
    def stimulate(self,padNum):
        try:
            padNum = str(padNum)
            ser.write((padNum).to_bytes(1,byteorder='big'))

        except:
            pass

    #電気刺激の強さをあげる
    def setLevelUp(self):
        try:
            ser.write(b'h')

        except:
            pass

    #電気刺激の強さを下げる
    def setLevelDown(self):
        try:
            ser.write(b'l')

        except:
            pass

    #振動させる
    def vibrate(self):
        try:
            ser.write(b'b')

        except:
            pass

    #ジェスチャ識別器の作成のために必要なデータを集める
    def gestureDataCollection(self,choseAll=True,*event):

        if choseAll:
            targetGesture1PR = np.array([0,0,0,0,0,0,0,0])
            targetGesture2PR = np.array([0,0,0,0,0,0,0,0])
        
        else:
            targetGesture1PR = np.array([0,0])
            targetGesture2PR = np.array([0,0])

        print("手を開いてください")

        #１つ目のジェスチャのデータ取得
        while len(targetGesture1PR) < 101:
            self.updatePhotosensors()

            #特に使うフォトリフレクタの番号の指定がない場合
            if choseAll == True:
                PRbuff = np.array(self.UHPR)
                
            #指定をした場合
            else:
                PRbuff = np.array(self.UHPR[:2])

            #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
            if len(PRbuff) < 8 and choseAll == True:
               pass

            elif len(PRbuff) < 2 and choseAll == False:
               pass
            
            else:
                len(PRbuff)
                targetGesture1PR = np.vstack((targetGesture1PR,PRbuff))

            print(len(targetGesture1PR))
            
        targetGesture1PR = np.delete(targetGesture1PR,0,0)
        
        print("3秒待機してください")
        time.sleep(3)

        print("手を閉じてください")
        
        #２つ目のジェスチャのデータ取得
        while len(targetGesture2PR) < 101:
            self.updatePhotosensors()

            #特に使うフォトリフレクタの番号の指定がない場合
            if choseAll == True:
                PRbuff = np.array(self.UHPR)

            else:
                PRbuff = np.array(self.UHPR[:2])

            #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
            if len(PRbuff) < 8 and choseAll == True:
                pass

            elif len(PRbuff) < 2 and choseAll == False:
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

        self.X_train,self.X_test = X[train_index],X[test_index]

        self.y_train,self.y_test = y[train_index],y[test_index]

        sc = StandardScaler()
        self.X_train_std = sc.fit_transform(self.X_train)
        

        self.X_test_std = sc.transform(self.X_test)



        
    #ジェスチャの正答率をチェックする
    def checkGesture(self,clfType="",*event):

        #ロジスティック回帰を用いてジェスチャの識別を行う
        def gestureLogisticClassifier(self,*event):
            self.clfLogistic.fit(self.X_train_std,self.y_train)
        
        #SVMを利用してジェスチャの識別を行う
        def gestureSVMClassifier(self,*event):
            self.clfSVM.fit(self.X_train_std,self.y_train)


        self.updatePhotosensors()
        print("チェック用のジェスチャを入力してください")
        time.sleep(3)

        if clfType == "logistic":
            gestureLogisticClassifier()

        elif clfType == "SVM":
            gestureSVMClassifier()

        #現在の手の状態をチェックする
        checkFlag = self.clfLogistic.predict(self.UHPR)
        print(checkFlag)

        if checkFlag == 0:
            self.nowGesture = "Close"
            print("手を閉じています")

        else:
            self.nowGesture = "Open"
            print("手を開いています")

#        predict = self.clfSVM.predict(self.X_test_std)
#        predict = self.clfLogistic.predict(self.UHPR[:2])
#        print(predict)
#
#        predict = self.clfLogistic.predict(self.y_train)
#        print(self.y_train)

        print(self.clfLogistic.score(self.X_test_std,self.y_test),"<----score")

       # from sklearn.metrics import confusion_matrix
       # print(confusion_matrix(self.y_test,self.),end="<-- confusion matrix")
        


    #csvとしてデータを吐き出す
    def csvOutput(self):
        f = open('output.csv','w')
        writer = csv.writer(f,lineterminator='\n')
        csvlist = []
        
        for data in self.X_test_std:
            print(data,end="data")
            csvlist.append(data)

        csvlist.append("---------")

        for data2 in self.y_test:
            csvlist.append(data2)

        print(self.X_test_std)
        print(self.y_test)

        writer.writerow(csvlist)

        f.close()



if __name__ == '__main__':
    uhand = UH()
    uhand.gestureDataCollection()
    uhand.checkGesture()

    for _ in range(1000):
        uhand.updatePhotosensors()
        uhand.checkGesture()
        print(uhand.UHPR)
