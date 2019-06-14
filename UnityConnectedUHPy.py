import serial
import time
from serial.tools import list_ports
import re
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from sklearn.metrics import accuracy_score

#マルチクラスのグラフ出力用
#import matplotlib.pyplot as plt
#from mlxtend.plotting import plot_decision_regions

import socket


#実験用
import datetime
import csv

class UH():
    
    def __init__(self):
        self.UHAngle = []
        self.UHPR = []
        self.UHGyroAccelData = []
        self.UHQuaternion = []
        #self.ser = serial.Serial('/dev/cu.usbserial-AK05D8TP', 115200,timeout=1)

        self.X_train_std,self.y_train,self.X_test_std,self.y_test = None,None,None,None

        #self.clfLogistic = LogisticRegression(penalty="l1",C=10)
        self.clfLogistic = LogisticRegression(C=1000)
        self.clfSVM = SVC(gamma=(2**-15),C=1000)

        self.nowGesture = None

        #Unlimitedhandとの接続に関する部分
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.timeout = 1

        ports = list_ports.comports()

        devices = []

        #どのジェスチャをしているか識別するためのもの
        self.checkFlag = None

        #文字入力のカウント
        self.charCount = 0

        self.oneCharFlag = False

        #1回目だけ識別器をフィットさせる
        self.oneTime = True

        #ジェスチャ識別のフィットが必要かどうか
        self.count = 0

        #ジェスチャ実験用
        self.firstData = True
        self.expCheck = 0.0
        self.expOutput = ["","","",""]
        self.f = None

        #Unityとの通信用
        self.dstip = "192.168.0.45"
        self.dstport = 12345
        self.message = b''

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

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

            self.ser.port = devices[3]
            
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
            print(self.UHQuaternion)

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
    def gestureDataCollection(self,gestureNum=2,*event):

        #ジェスチャ数を増やしたいときにつかすべき部分1
        targetGesture1PR = np.array([[0,0,0,0,0,0,0,0]])
        targetGesture2PR = np.array([[0,0,0,0,0,0,0,0]])
        targetGesture3PR = np.array([[0,0,0,0,0,0,0,0]])
        targetGesture4PR = np.array([[0,0,0,0,0,0,0,0]])
        targetGesture5PR = np.array([[0,0,0,0,0,0,0,0]])
        targetGesture6PR = np.array([[0,0,0,0,0,0,0,0]])

        #１つ目のジェスチャのデータ取得
        print("手を開いてください")
        print("5秒待ちます")
        time.sleep(5)

        while len(targetGesture1PR) < 101:
            self.updatePhotosensors()
            PRbuff = np.array(self.UHPR)
                
            #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
            if len(PRbuff) < 8:
                pass

            else:
                targetGesture1PR = np.vstack((targetGesture1PR,PRbuff))

            print(len(targetGesture1PR))
            
        #1個目のデータは不安定なので削除
        targetGesture1PR = np.delete(targetGesture1PR,0,0)
        

        #２つ目のジェスチャのデータ取得
        print("手を握ってください")
        print("5秒待ちます")
        time.sleep(5)

        while len(targetGesture2PR) < 101:
            self.updatePhotosensors()
            PRbuff = np.array(self.UHPR)

            #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
            if len(PRbuff) < 8:
                pass

            else:
                targetGesture2PR = np.vstack((targetGesture2PR,PRbuff))

            print(len(targetGesture2PR))

        #1個目のデータは不安定なので削除
        targetGesture2PR = np.delete(targetGesture2PR,0,0)
        
        #3つ目のジェスチャのデータ取得
        if gestureNum >=  3:
            print("つまんでください")
            print("5秒待ちます")
            time.sleep(5)

            while len(targetGesture3PR) < 101:
                self.updatePhotosensors()
                PRbuff = np.array(self.UHPR)
    
                #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
                if len(PRbuff) < 8:
                    pass
    
                else:
                    targetGesture3PR = np.vstack((targetGesture3PR,PRbuff))

                print(len(targetGesture3PR))
    
            #1個目のデータは不安定なので削除
            targetGesture3PR = np.delete(targetGesture3PR,0,0)
        
        if gestureNum >= 4:
            print("ピストルの形にしてください")
            print("5秒待ちます")
            time.sleep(5)

            while len(targetGesture4PR) < 101:
                self.updatePhotosensors()
                PRbuff = np.array(self.UHPR)
                    
                #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
                if len(PRbuff) < 8:
                    pass
    
                else:
                    targetGesture4PR = np.vstack((targetGesture4PR,PRbuff))
    
                print(len(targetGesture4PR))
                
            #1個目のデータは不安定なので削除
            targetGesture4PR = np.delete(targetGesture4PR,0,0)

        if gestureNum >= 5:
            print("狐の形にしてください")
            print("5秒待ちます")
            time.sleep(5)

            while len(targetGesture5PR) < 101:
                self.updatePhotosensors()
                PRbuff = np.array(self.UHPR)
                    
                #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
                if len(PRbuff) < 8:
                    pass
    
                else:
                    targetGesture5PR = np.vstack((targetGesture5PR,PRbuff))
    
                print(len(targetGesture5PR))
                
            #1個目のデータは不安定なので削除
            targetGesture5PR = np.delete(targetGesture5PR,0,0)
        
        if gestureNum >= 6:
            print("イェーイの形にしてください")
            print("5秒待ちます")
            time.sleep(5)

            while len(targetGesture6PR) < 101:
                self.updatePhotosensors()
                PRbuff = np.array(self.UHPR)
                    
                #フォトリフレクタから撮ってきたリストの要素の数が足りない場合の対応
                if len(PRbuff) < 8:
                    pass
    
                else:
                    targetGesture6PR = np.vstack((targetGesture6PR,PRbuff))
    
                print(len(targetGesture6PR))
                
            #1個目のデータは不安定なので削除
            targetGesture6PR = np.delete(targetGesture6PR,0,0)

        if gestureNum == 2:
            y1 = np.zeros(100,dtype=int)
            y2 = np.ones(100,dtype=int)
            self.X = np.r_[targetGesture1PR,targetGesture2PR]
            self.X.reshape(-1,1)
            self.y = np.r_[y1,y2]
        
        elif gestureNum == 3:
            y1 = np.zeros(100,dtype=int)
            y2 = np.ones(100,dtype=int)
            y3 = y2+np.ones(100,dtype=int)
            self.X = np.r_[targetGesture1PR,targetGesture2PR,targetGesture3PR]
            self.y = np.r_[y1,y2,y3]

        elif gestureNum == 4:
            y1 = np.zeros(100,dtype=int)
            y2 = np.ones(100,dtype=int)
            y3 = y2+np.ones(100,dtype=int)
            y4 = y3+np.ones(100,dtype=int)
            self.X = np.r_[targetGesture1PR,targetGesture2PR,targetGesture3PR,targetGesture4PR]
            self.y = np.r_[y1,y2,y3,y4]

        elif gestureNum == 5:
            y1 = np.zeros(100,dtype=int)
            y2 = np.ones(100,dtype=int)
            y3 = y2+np.ones(100,dtype=int)
            y4 = y3+np.ones(100,dtype=int)
            y5 = y4+np.ones(100,dtype=int)
            self.X = np.r_[targetGesture1PR,targetGesture2PR,targetGesture3PR,targetGesture4PR,targetGesture5PR]
            self.y = np.r_[y1,y2,y3,y4,y5]

        elif gestureNum == 6:
            y1 = np.zeros(100,dtype=int)
            y2 = np.ones(100,dtype=int)
            y3 = y2+np.ones(100,dtype=int)
            y4 = y3+np.ones(100,dtype=int)
            y5 = y4+np.ones(100,dtype=int)
            y6 = y5+np.ones(100,dtype=int)
            self.X = np.r_[targetGesture1PR,targetGesture2PR,targetGesture3PR,targetGesture4PR,targetGesture5PR,targetGesture6PR]
            self.y = np.r_[y1,y2,y3,y4,y5,y6]

        print(len(self.X),len(self.y))

#        ss = ShuffleSplit(n_splits=1,
#                          train_size=0.7,
#                          test_size=0.3,
#                          random_state=0
#                          )
#        
#        train_index, test_index = next(ss.split(self.X,self.y))
#
#        self.X_train,self.X_test = self.X[train_index],self.X[test_index]
#
#        self.y_train,self.y_test = self.y[train_index],self.y[test_index]
#
#        sc = StandardScaler()
#        
#        sc2 = StandardScaler()
#
#        
#        self.X_std = sc2.fit_transform(self.X)
#
#        self.X_train_std = sc.fit_transform(self.X_train)
#        
#
#        self.X_test_std = sc.transform(self.X_test)


    #ロジスティック回帰を用いてジェスチャの識別を行う
    def gestureLogisticClassifier(self,*event):
        self.clfLogistic.fit(self.X,self.y)
        
        return 0

    #SVMを利用してジェスチャの識別を行う
    def gestureSVMClassifier(self,*event):
        self.clfSVM.fit(self.X,self.y)

        return 0


        
#    def checkGesture(self,clfType="logistic",*event):
    def checkGesture(self,clfType="logistic",*event):

        self.updatePhotosensors()
        print("                                        ")
        print("チェック用のジェスチャを入力してください")
        print("5秒待ちます")

        time.sleep(0.1)
        
        #一回めのみ識別器のフィットを行う
        if self.count == 0:
            if clfType == "logistic":
                self.gestureLogisticClassifier()

            elif clfType == "SVM":
                self.gestureSVMClassifier()

        self.count += 1

        #現在の手の状態をチェックする
        #self.checkFlag = self.clfLogistic.predict(self.UHPR)
        if clfType == "logistic":
            self.updatePhotosensors()
            print(self.clfLogistic.predict(np.array(self.UHPR).reshape(1,-1)))
            self.checkFlag = self.clfLogistic.predict(np.array(self.UHPR).reshape(1,-1))

        elif clfType == "SVM":
            self.updatePhotosensors()
            print(self.clfSVM.predict(np.array(self.UHPR).reshape(1,-1)))
            self.checkFlag = self.clfSVM.predict(np.array(self.UHPR).reshape(1,-1))


        if self.checkFlag == 0:
            self.expCheck = 0
            self.nowGesture = b'0'
            print("手を開いています")

        elif self.checkFlag == 1:
            self.expCheck = 1
            self.nowGesture = b'1'
            print("手を握っています")

        elif self.checkFlag == 2:
            self.expCheck = 2
            self.nowGesture = b'2'
            print("つまんでいます")

        elif self.checkFlag == 3:
            self.expCheck = 3
            self.nowGesture = b'3'
            print("ピストルの形です")

        elif self.checkFlag == 4:
            self.expCheck = 4
            self.nowGesture = b'4'
            print("狐の形です")

        elif self.checkFlag == 5:
            self.expCheck = 5
            self.nowGesture = b'5'
            print("イェーイの形です")

        self.expOutput.append(self.expCheck)

#        predict = self.clfSVM.predict(self.X_test_std)
#        predict = self.clfLogistic.predict(self.UHPR[:2])
#        print(predict)
#
#        predict = self.clfLogistic.predict(self.y_train)
#        print(self.y_train)

#        if clfType == "logistic":
#            print(self.clfLogistic.score(self.X,self.y),"<----Accuracy Score")
#
#        elif clfType == "SVM":
#        print(self.clfSVM.score(self.X,self.y),"<--------Accuracy Score")

       # from sklearn.metrics import confusion_matrix
       # print(confusion_matrix(self.y_test,self.),end="<-- confusion matrix")
        
#    def graphUHPR(self):
#        plot_decision_regions(X=self.X_std[:,[0,1]],y=self.y,clf=self.clfLogistic)
#        plt.show()


        return 0

    #csvとしてデータを吐き出す

    def csvOutput(self):
        self.f = open("gestureCheck.csv",'a')
        if self.firstData:
            for i in range(4):
                self.f.write(self.expOutput[i]+',')
                self.firstData = False
        self.f.write(str(self.expCheck)+',')



if __name__ == '__main__':
    uhand = UH()
    uhand.gestureDataCollection(gestureNum=2)
    uhand.gestureSVMClassifier()

    for i in range(10000):
        uhand.checkGesture()
        #uhand.sock.sendto(bytes(uhand.nowGesture,encoding='utf-8',errors='replace'),(uhand.dstip,uhand.dstport))
        uhand.sock.sendto(uhand.nowGesture,(uhand.dstip,uhand.dstport))

        time.sleep(0.1)
